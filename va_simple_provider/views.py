"""
    Handle the URL requests.

    On initialization the module is initializated using parameters
    in file application.ini, section routing.

    The application is designed to handle requests for only one code.

    The module handle the requests issued using only specific methods:
    POST, GET, ...
"""
# HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

import re
import os
import logging
import numbers
import time

from flask import request, json, abort, render_template, Response, send_from_directory
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import HTTPException
from configparser import ConfigParser
from json.decoder import JSONDecodeError
from collections.abc import Mapping

from va_simple_provider import app, configuration_directory

from va_simple_provider.custom_exceptions import BaseCustomException
from va_simple_provider.custom_exceptions import AppCustomException
from va_simple_provider import db_utils
from va_simple_provider.controllers import code_handler

__max_param_len = None
FORMAT_TAG = "-out_format"
HTML_FORMAT = "html"
JSON_FORMAT = "json"

def __config():
  """
  Set the private internal parameters for the whole module.

  The following parameters are read from file 'application.ini',
  section 'routing':
    succesfull_job_submit_url
    max_allowed_parameter_len
    max_allowed_request_body_size
  """

  filename = os.path.join(configuration_directory, 'application.ini')
  section = 'routing'

  global __max_param_len
  max_param_len_key = 'max_allowed_parameter_len'

  max_body_size_key = 'max_allowed_request_body_size'

  # create a parser
  parser = ConfigParser()
  # read config file
  parser.read(filename)

  # get section parameters
  section_params = {}
  if parser.has_section(section):
    params = parser.items(section)
    for param in params:
      section_params[param[0]] = param[1]
  else:
    raise AppCustomException(
      "Section '{0}' not found in file '{1}'.".format(
        section, os.path.abspath(filename)
      )
    )

  if (not (max_param_len_key in section_params.keys())):
    raise AppCustomException(
      "Parameter '{0}' not found in section '{1}' in file '{2}'.".format(
        max_param_len_key, section, os.path.abspath(filename)
      )
    )
  try:
    __max_param_len = int(section_params[max_param_len_key])
  except:
    raise AppCustomException(
      "Parameter '{0}' in section '{1}' in file '{2}' "
      "must be an integer.".format(
        max_param_len_key, section, os.path.abspath(filename)
      )
    )

  if (not (max_body_size_key in section_params.keys())):
    raise AppCustomException(
      "Parameter '{0}' not found in section '{1}' in file '{2}'.".format(
        max_body_size_key, section, os.path.abspath(filename)
      )
    )
  if not re.match("^[0-9 *]*$", section_params[max_body_size_key]):
    raise AppCustomException(
      "Characters allowed for parameter '{0}' in section '{1}' "
      "in file '{2}' are only digit, *, space.".format(
        max_body_size_key, section, os.path.abspath(filename)
      )
    )
  app.config['MAX_CONTENT_LENGTH'] = (
    int(eval(section_params[max_body_size_key], {}))
  )

  return
__config()

def __check_parameter_name(param_name: str):
  """
  Perform some parameters name check common to files and data.
  """

  if (len(param_name) > __max_param_len):
    err_msg = (
      "Parameter name exceed maximum allowed len: '{0}...'."
    ).format(param_name[0:(__max_param_len-1)])
    abort(Response(json.dumps({'Message': err_msg}), 400))

@app.route('/execute', methods=['POST'])
def do_execute():
  """
  Handle the request to submit a new job with parameters passed as
  attributes of an object in json format.

  Only the following Content-Type are allowed:
  -) text/plain
  -) application/json

  If succesfull the request is redirected to a page
  with the ID of the accepted job.
  If unsuccesfull the request is aborted and redirected to error page
  with status code 400 and possibly a meaningfull description.
  """

  try:
    content_type = request.headers.get('Content-Type')
    if not content_type.startswith('application/json'):
      err_msg = "Unaccepted content type: '{0}'.".format(content_type)
      abort(Response(json.dumps({'Message': err_msg}), 400))
    try:
      json_body = json.loads(request.data)
      code_input_params = json_body['code_input_params']
      application_params =  json_body['application_params']
      request_id = application_params['job_id']
      synch_execution = application_params.get('synch_execution', True)
    except (JSONDecodeError, TypeError) as error:
      # Here logging is required, as we do not want to return
      # the full JSON to the user.
      err_msg = "Malformed JSON string for \'inputs\'."
      app.logger.warning(err_msg + str(error))
      abort(Response(json.dumps({'Message': err_msg}), 400))

    if not isinstance(code_input_params, Mapping):
      err_msg = "JSON string does not represent an object " \
                "(pairs of name/value)."
      abort(Response(json.dumps({'Message': err_msg}), 400))
    
    string_parameters = {}
    for parameter_key in code_input_params.keys():
      __check_parameter_name(parameter_key)
      if isinstance(code_input_params[parameter_key], str):
        string_parameters[parameter_key] = code_input_params[parameter_key]
      elif isinstance(code_input_params[parameter_key], list):
        string_parameters[parameter_key] = [
          str(v) for v in code_input_params[parameter_key]
        ]
      elif isinstance(code_input_params[parameter_key], bool):
        string_parameters[parameter_key] = ""
      elif isinstance(code_input_params[parameter_key], numbers.Number):
        string_parameters[parameter_key] = str(code_input_params[parameter_key])
      else:
        err_msg = "Unexpected value for parameter '{0}.".format(parameter_key)
        abort(Response(json.dumps({'Message': err_msg}), 400))

    code_handler.submit_form_request(string_parameters, request_id)
  except HTTPException as error:
    raise error
  except BaseCustomException as error:
    app.logger.warning(str(error))
    abort(Response(json.dumps({'Message': str(error)}), 400))
  except AppCustomException as error:
    app.logger.error(str(error))
    err_msg = "Application error. Please report to the " \
              "application manager with date and time of the problem."
    abort(Response(json.dumps({'Message': err_msg}), 400))
  except Exception as error:
    app.logger.error(str(error), exc_info=True)
    err_msg = "Please report to the application manager " \
              "with date and time of the problem."
    abort(Response(json.dumps({'Message': err_msg}), 400))


  MAX_WAIT = 2.0      # secondi di attesa massima per far partire il thread
  SLEEP = 0.5         # polling interval
  start = time.monotonic()
  while True:
    job_info = get_job_info(request_id)
    if job_info['job_info']['start_processing'] is not None:
      break

    # possibile che il thread sia in partenza
    if time.monotonic() - start > MAX_WAIT:
      # thread non partito in tempi ragionevoli:
      err_msg = "Job not started. Please report to the application manager " \
                "with date and time of the problem."
      app.logger.error(err_msg, exc_info=True)
      abort(Response(json.dumps({'Message': err_msg}), 400))
      
    time.sleep(SLEEP)

  # Il thread è partito
  if not synch_execution:
    return {}
  else:
    while True:
      job_info = get_job_info(request_id)
      if job_info['job_info']['end_processing'] is not None:
        # Nota: se ci fosse un problema per il thread di connettersi
        # e scrivere sul DB, allora fallirebbe anche get_job_info()
        # con una eccezione ed abort(), terminando la richiesta.
        return job_info
      time.sleep(SLEEP)

@app.route('/job_info/<string:job_id>', methods=['GET'])
def get_job_info(job_id: str):
    """
    Return input parameters, the status of the requested
    elaboration, and possibly the output.
    """

    job_info = code_handler.get_job_info(job_id)
    if job_info:
      params = code_handler.get_request_parameters(job_id)
    else:
      err_msg = "Data on job_id  {0} not present.".format(job_id)
      abort(Response(json.dumps({'Message': err_msg}), 400))

    code_params = {}
    for param in params:
      code_params[param["name"]] = param["value"]
            
    return {
      "job_id": job_id,
      "job_info": {
          "received": job_info["received"],
          "start_processing": job_info["start_processing"],
          "end_processing": job_info["end_processing"],
          "exit_code": job_info["exit_code"],
          "std_out": job_info["std_out"],
          "std_err": job_info["std_err"]},
      "params": code_params
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  return render_template('home.html')
