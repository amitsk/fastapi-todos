FROM python:3.8-slim  as base

# https://sourcery.ai/blog/python-docker/

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends g++

# Install python dependencies in /.venv
# https://pipenv.pypa.io/en/latest/advanced/
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy


FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser

ENV APP_MODULE="fastapi_todos.main:app"
ENV PORT 8000
EXPOSE ${PORT}
# Install application into container
COPY fastapi_todos  fastapi_todos/
COPY start.sh .
RUN chmod +x ./start.sh
COPY gunicorn.conf.py   .
USER appuser
ENV PYTHONPATH=/home/appuser:$PYTHONPATH
CMD ["/home/appuser/start.sh"]