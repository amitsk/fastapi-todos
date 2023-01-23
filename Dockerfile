FROM python:3.11-slim  as base

# https://sourcery.ai/blog/python-docker/

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1


FROM base AS python-deps

## Install pipenv and compilation dependencies
#RUN pip install pipenv
#RUN apt-get update && apt-get install -y --no-install-recommends g++
# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm


# copy files
#COPY pyproject.toml pdm.lock README.md /project/
# Install python dependencies in /.venv
# https://pipenv.pypa.io/en/latest/advanced/
#COPY Pipfile.donotuse .
#COPY Pipfile.lock.donotuse .
#RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy
RUN make test

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
COPY gunicorn.conf.py .
USER appuser
ENV PYTHONPATH=/home/appuser:$PYTHONPATH
CMD ["./start.sh"]