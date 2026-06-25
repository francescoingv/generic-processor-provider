# ------------------------------------------------------------------------------
# Dockefile container TEMPLATE for generic application
#
# This image:
# - installs the generic Flask application
# - ### TODO: complete for WPS-specific sources
# - builds all configuration at build-time
# ------------------------------------------------------------------------------

FROM python:3.12

LABEL maintainer="francesco.martinelli@ingv.it"

# ------------------------------------------------------------------------------
# BUILD-TIME ARGUMENTS (CONTRACT)
# ------------------------------------------------------------------------------

ARG IP_ADDRESS_POSTGRES_SERVER
ARG PORT_POSTGRES_SERVER
ARG ID_SERVICE
ARG BASE_DIRECTORY
ARG SUPPRESS_STDOUT
ARG COMMAND_LINE

# ------------------------------------------------------------------------------
# ARG VALIDATION
# ------------------------------------------------------------------------------

RUN for v in \
    IP_ADDRESS_POSTGRES_SERVER \
    PORT_POSTGRES_SERVER \
    ID_SERVICE \
    BASE_DIRECTORY \
    SUPPRESS_STDOUT \
    COMMAND_LINE \
; do \
    test -n "$(eval echo \$$v)" || \
      (echo "<<ERROR>> Required build argument '$v' not set." && exit 1); \
done

# Ensure COMMAND_LINE contains only single quotes
RUN /bin/bash -c 'double_quotes_number=$(grep --fixed-strings --count "\"" - <<< "$COMMAND_LINE"); \
  if [ $double_quotes_number -ne 0 ]; \
  then (echo "COMMAND_LINE contains double quotes, only single quotes allowed." && false); \
  fi'

# ------------------------------------------------------------------------------
# SYSTEM DEPENDENCIES
# Install sistem dependencies (OS)
# TODO: add installation of specific libraries.
# ------------------------------------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        postgresql-client \
        ## Add specific libraries as required
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------------------------
# PYTHON ENVIRONMENT CONFIGURATION
# ------------------------------------------------------------------------------

## Configure virtual environments and directories
## - Create virtual environments for Flask and WPS in newly created /venvs dir:
RUN mkdir -p /venvs \
    && python -m venv /venvs/flask /venvs/specific \
    && mkdir -p /apps/generic /apps/specific

## Set flask Venv as default.
## - Note: adding bin directory of venv to PATH is no more required to call "source activate".
ENV PATH="/venvs/flask/bin:$PATH"

# ------------------------------------------------------------------------------
# INSTALLATION OF THE GENERIC APP (Flask)
# ------------------------------------------------------------------------------

RUN git clone \
    https://github.com/francescoingv/generic-processor-provider.git \
    /apps/generic

# - Using WORKDIR next commands are relative to this folder.
WORKDIR /apps/generic

# Copy Docker template configuration files into final application location
RUN cp docker/application.ini va_simple_provider/application.ini \
 && cp docker/database.ini va_simple_provider/database.ini
 
# Injection of configuration parameters (at build time).
# Substitute build-time variables
RUN sed -i 's/\$IP_ADDRESS_POSTGRES_SERVER\$/'${IP_ADDRESS_POSTGRES_SERVER}'/g' ./va_simple_provider/database.ini \
 && sed -i 's/\$PORT_POSTGRES_SERVER\$/'${PORT_POSTGRES_SERVER}'/g' ./va_simple_provider/database.ini \
 && sed -i 's/\$ID_SERVICE\$/'${ID_SERVICE}'/g' ./va_simple_provider/application.ini \
 && sed -i 's#\$BASE_DIRECTORY\$#'${BASE_DIRECTORY}'#g' ./va_simple_provider/application.ini \
 && sed -i 's#\$SUPPRESS_STDOUT\$#'${SUPPRESS_STDOUT}'#g' ./va_simple_provider/application.ini \
 && sed -i "s@\\\$COMMAND_LINE\\\$@${COMMAND_LINE}@g" ./va_simple_provider/application.ini    

# Install Python dependencies
# - Thanks to PATH above, 'pip' refer to what is in /venvs/flask
# - Thanks to WORKDIR above, 'requirements.txt' refer to /apps/generic
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------------------
# WPS SPECIFIC INSTALLATION 
# ------------------------------------------------------------------------------

# TODO: Application specific

# ------------------------------------------------------------------------------
# NETWORKING & ENV
# ------------------------------------------------------------------------------

EXPOSE 5000

# Possibly not used: verify if not needed and in case remove:
ENV ENV_IP_ADDRESS_POSTGRES_SERVER=${IP_ADDRESS_POSTGRES_SERVER}

# ------------------------------------------------------------------------------
# START THE SERVICE
# ------------------------------------------------------------------------------

# Start the service:
# - Thanks to PATH above, 'python' refer to what is inside /venvs/flask
# - Thanks to WORKDIR above, /apps/generic, flask application start from the correct folder

# NOTE:
# Flask is started via CMD instead of ENTRYPOINT to keep
# the entire execution logic self-contained inside the image,
# without requiring external scripts or host-side commands.
CMD ["python", "-m", "flask", "--app", "va_simple_provider", "run", "--host=0.0.0.0"]


