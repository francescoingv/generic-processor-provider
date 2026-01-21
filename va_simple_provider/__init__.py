# Module initialization
# #####################

import os

from flask import Flask
from logging.config import fileConfig

# Include handling custom exceptions
from va_simple_provider.custom_exceptions import BaseCustomException

# Create instance of Flask in variable named "app".
app = Flask(__name__)

# from werkzeug.middleware.proxy_fix import ProxyFix
# app.wsgi_app = ProxyFix(
#     app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
# )

configuration_directory = os.path.dirname(os.path.abspath(__file__))

fileConfig(os.path.join(configuration_directory, 'logging.cfg'))
app.logger.info('Application started...')

try:
    # This import from "va_simple_provider" module must come after creating "app" variable,
    # so that views can import app variable
    from va_simple_provider import views
except (Exception) as error:
    app.logger.critical("Initialization error: " + str(error))
    raise


# End of initialization
