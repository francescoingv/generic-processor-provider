"""
    Provide the functions to interact with the code.


"""

import os
import threading
import subprocess
import ast

from cgi import FieldStorage

from configparser import ConfigParser

from va_simple_provider import app, configuration_directory
from va_simple_provider import db_utils
from va_simple_provider.custom_exceptions import AppCustomException
from va_simple_provider.custom_exceptions import BaseCustomException

__id_service = None
__command_line = None
__file_root_directory = None

def __config():
  """
  Set the private internal parameters for the whole module.

  The following parameters are read from file 'application.ini', 
  section 'executable':
    id_service
    command_line
    file_root_directory
  """

  filename = os.path.join(configuration_directory, 'application.ini')
  section = 'executable'

  global __id_service
  id_service_key = 'id_service'

  global __command_line
  command_line_key = 'command_line'

  global __file_root_directory
  file_root_directory_key = 'file_root_directory'

  global __suppress_stdout
  suppress_stdout_key = 'suppress_stdout'

  parser = ConfigParser()
  parser.read(filename)

  section_parameters = {}
  if parser.has_section(section):
    params = parser.items(section)
    for param in params:
      section_parameters[param[0]] = param[1]
  else:
    raise AppCustomException(
      "Section '{0}' not found in file '{1}'.".format(
        section, os.path.abspath(filename)
      )
    )
  
  if (not (id_service_key in section_parameters.keys())):
    raise AppCustomException(
      "Parameter '{0}' not found in section '{1}' in file '{2}'.".format(
        id_service_key, section, os.path.abspath(filename)
      )
    )
  __id_service = section_parameters[id_service_key]

  if (not (file_root_directory_key in section_parameters.keys())):
    raise AppCustomException(
      "Parameter '{0}' not found in section '{1}' in file '{2}'.".format(
        file_root_directory_key, section, os.path.abspath(filename)
      )
    )
  __file_root_directory = section_parameters[file_root_directory_key]

  if (not (command_line_key in section_parameters.keys())):
    raise AppCustomException(
      "Parameter '{0}' not found in section '{1}' in file '{2}'.".format(
        command_line_key, section, os.path.abspath(filename)
      )
    )
  tmp_command_line = ast.literal_eval(section_parameters[command_line_key])
  if (type(tmp_command_line) == type([])):
    __command_line = tmp_command_line
  else:
    __command_line = [tmp_command_line]

  if (suppress_stdout_key in section_parameters.keys()):
    __suppress_stdout = section_parameters[suppress_stdout_key]
  else:
    __suppress_stdout = False

  return
__config()

def __callable_function(request_id, command_line_args, base_working_dir):
  """
  Function called as separate thread to invoke (run) the requested code.

  The function record the state of the request on the DB:
  -) before calling the code
  -) after the end of the execution
  The end of processing will be recorded also if
  the code ends with exceptions.
  """

  command_line = []
  command_line.extend(command_line_args)

  try:
    with db_utils.get_db_connection() as conn:
      try: 
        db_utils.record_started_request(conn, request_id)
      except Exception as ex:
        db_utils.record_failed_request(conn, request_id, str(ex))
  except Exception as ex:
    app.logger.error(
      "Request failed on start. Request id = {0}. {1}".format(
        request_id, str(ex)
      ),
      exc_info=True
    )
    # There is nothing else to do.
    return

  outcome = subprocess.run(
    command_line,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=base_working_dir
  )

  try:
    with db_utils.get_db_connection() as conn:
      db_utils.record_completed_request(conn, request_id, outcome, __suppress_stdout)
  except Exception as ex:
    app.logger.error(
      "Request completed but was not registered to the DB. "
      "Request id = {0}. {1}".format(
        request_id, str(ex)
      ),
      exc_info=True
    )

  return

def __submit_request(request_id, command_line, base_working_dir) -> None:
  """
  Prepare the new thread to call the code asynchronously; 
  update the request state on the DB.

  Return the timestamp when the request was received.
  """

  # per interrompere provare:
  # https://stackoverflow.com/questions/28633357/kill-python-thread-using-os
  t = threading.Thread(
    target=__callable_function,
    name=request_id,
    kwargs={
      'request_id' : request_id,
      'command_line_args': command_line,
      'base_working_dir': base_working_dir,
    }
  )
  t.start()

  return

def _get_root_local_file_dir(request_id: str) -> str:
  """
  Get the base directory where to write the files associated to the request.
  """

  return os.path.join(__file_root_directory, request_id, "")

def submit_form_request(string_parameters: "dict[str, str]", request_id: str) -> None:
  """
  Accept a request having the parameters as dictionary items.

  If the function fails to record the parameters
  the request is removed from DB.
  If the function succeded a separate thread is initialized and started.
  
  The values  may either be empty (i.e. flag parameters), or strings.
  """

  command_line_args = []
  command_line_args.extend(__command_line)

  with db_utils.get_db_connection() as conn:
    db_utils.add_new_request(conn, __id_service, request_id)

    base_local_file_dir = _get_root_local_file_dir(request_id)
    if not os.path.exists(base_local_file_dir):
      os.makedirs(base_local_file_dir)

    try:
      for param_name, param_value in string_parameters.items():
        # Save parameters to DB:
        if isinstance(param_value, list):
            db_value = " ".join(param_value)
        else:
            db_value = param_value
        db_utils.add_request_parameter(
            conn, request_id, param_name, db_value
        )

        # Add command line parameters
        command_line_args.append(param_name)
        if isinstance(param_value, list):
            command_line_args.extend(param_value)
        else:
            command_line_args.append(param_value)
    except Exception as ex:
      app.logger.error(
        "Request not completely submitted: aborting. " + str(ex)
      )
      db_utils.abort_request(conn, request_id)
      raise ex
        
  __submit_request(request_id, command_line_args, base_local_file_dir)
  
  return

def get_request_parameters(request_id: str):
  """
  Returns a list of dictionaries with informations on the request parameters.

  The parameters set by the specific request and their customs values,
  are returned.

  Keys returned in each dictionary are: name, value.
  """
  
  with db_utils.get_db_connection() as conn:
    parameters = db_utils.get_request_parameters(conn, request_id)

  return parameters

def get_job_info(request_id: str):
  """
  Returns a dictionary with job specific information.

  If the id_request is not present on the DB for this code,
  then returns None.
  """
  
  with db_utils.get_db_connection() as conn:
    job_info = db_utils.get_job_info(conn, request_id)

  if job_info and job_info['service'] != __id_service:
    app.logger.warning(
      "Requested info on job '{0}' running service '{1}': "
      "application configured for service '{2}'.".format(
        request_id, job_info['service'], __id_service
      )
    )
    return None
  else:
    return job_info

