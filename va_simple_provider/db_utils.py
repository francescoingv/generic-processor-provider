
import os

# Imprt library to interact with PostgreSQL
import psycopg2
import psycopg2.extras

from configparser import ConfigParser

from va_simple_provider import app, configuration_directory
from va_simple_provider.custom_exceptions import AppCustomException

# Internal use to module only:
__database_connection_parameters = None


def __config():
  """
  Set the private internal parameters for the whole module.

  The following parameters are read from file 'database.ini':
    all section 'postgresql' into __database_connection_parameters
  """
  
  filename = os.path.join(configuration_directory, 'database.ini')

  section_db = 'postgresql'
  global __database_connection_parameters

  # create a parser
  parser = ConfigParser()
  # read config file, default to database.ini
  parser.read(filename)

  # get database section
  db = {}
  if parser.has_section(section_db):
    params = parser.items(section_db)
    for param in params:
      db[param[0]] = param[1]
  else:
    raise AppCustomException(
      "Section '{0}' not found in file {1}'.".format(
        section_db, os.path.abspath(filename)
      )
    )
  __database_connection_parameters = db

  try:
    # Test connection parameters:
    test_query = """SELECT version()"""
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(test_query)
        cur.fetchone()
  except (Exception) as ex:
    app.logger.error('Test connecting to DB failed: ' + str(ex))
    raise AppCustomException(
      'Test connecting to DB failed.'
    ) from ex

  return

def get_db_connection():
  """
  Get and return a new connection to the DB.
  """
  try:
    conn = psycopg2.connect(**__database_connection_parameters)
  except (Exception) as ex:
    app.logger.error('Connecting to DB failed: ' + str(ex))
    raise AppCustomException(
      'Test connecting to DB failed.'
    )
  
  return conn

def add_new_request(conn, service_id: str, request_id: str) -> None:
  """
  Create a new record for the request and return the ID.
  """

  query_insert = """INSERT INTO request(id, service) VALUES(%s, %s)"""

  with conn.cursor() as cur:
      cur.execute(query_insert, (request_id, service_id))
      conn.commit()

def add_request_parameter(
    conn, request_id: str, param_name: str, param_value: str) -> None:
  """
  Add a parameter to the request.
  """
  query_insert = """INSERT INTO request_parameter(request_id, name, value)
                    VALUES(%s, %s, %s)"""
  with conn.cursor() as cur:
    cur.execute(query_insert, (request_id, param_name, param_value))
    conn.commit()

def get_request_parameters(conn, request_id: str):
  """
  Returns a list of dictionaries with the informations
  for the parameters used by the request.
  
  Informations returned as keys to the dictionaries are:
  name, value.
  """
  with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    query_select = """SELECT name, value
                        FROM request_parameter
                        WHERE request_id = %s"""
    query_params = [request_id]
    cur.execute(query_select, query_params)
    return cur.fetchall()
    
def abort_request(conn, request_id: str) -> None:
  """
  Remove the whole request from the DB.
  """

  # Clean the connection where are possible pending operation.
  conn.commit()

  query_delete_params = """DELETE FROM request_parameter 
                           WHERE request_id = %s"""
  with conn.cursor() as cur:
    cur.execute(query_delete_params, (request_id, ))
  # Commit must include the deletion of both request_parameter 
  # and request together.

  query_delete_request = """DELETE FROM request WHERE id = %s"""
  with conn.cursor() as cur:
    cur.execute(query_delete_request, (request_id, ))

  # ONLY if all above was succesful it is possible to commit.
  conn.commit()

def record_started_request(conn, request_id: str):
  """
  Update the request status of the request on the DB at start of processing.
  """
  query_update = """UPDATE request 
                    SET start_processing = NOW() 
                    WHERE id = %s"""
  with conn.cursor() as cur:
    cur.execute(query_update, (request_id, ))
    conn.commit()
      
def record_failed_request(conn, request_id, error_message):
  """
  Update the request status of the request on the DB
  for a request failed before start of execution.

  Also a possible error message is set in std_err field.
  """
  query_update = """UPDATE request 
                    SET (end_processing, exit_code, std_out, std_err)
                        = (NOW(), -1, '', %s)
                    WHERE id = %s"""
  with conn.cursor() as cur:
    cur.execute(query_update, (error_message, request_id))
    conn.commit()
      
def record_completed_request(conn, request_id, outcome, suppress_stdout):
  """
  Update the request status of the request on the DB
  for a completed request.

  All returned information (exit code, std_out, std_err)
  are stored in the DB.
  """
  query_update = """UPDATE request 
                    SET (end_processing, exit_code, std_out, std_err)
                        = (NOW(), %s, %s, %s)
                    WHERE id = %s"""
  with conn.cursor() as cur:
    cur.execute(
      query_update,
      (outcome.returncode, outcome.stdout if (not suppress_stdout) else "",
       outcome.stderr, request_id)
    )
    conn.commit()
      
def get_job_info(conn, id_request: str):
  """
  Returns a dictionary with the informations of the job status as on the DB.
  """
  with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
    query_select = """SELECT service, received, start_processing, 
                             end_processing, time_to_clean, 
                             exit_code, std_out, std_err
                      FROM request
                      WHERE id = %s"""
    cur.execute(query_select, (id_request, ))
    return cur.fetchone()

# Run the configuration of the module as initialization step.
__config()
