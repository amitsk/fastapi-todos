FROM python:3.11-slim  as base

#https://pdm.fming.dev/latest/usage/advanced/#use-pdm-in-a-multi-stage-dockerfile
# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Turns off writing .pyc files; superfluous on an ephemeral container.
ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

FROM base AS builder


RUN apt-get update && apt-get install -y --no-install-recommends g++
# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm


COPY pyproject.toml .
COPY  pdm.lock .
RUN pdm sync --prod


FROM base AS runtime

# Extra python env
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

ENV PATH="/.venv/bin:$PATH"
ENV APP_MODULE="fastapi_todos.main:app"
ENV PORT 8000
ENV PYTHONPATH=/home/appuser:$PYTHONPATH

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Copy virtual env from python-deps stage
COPY --from=builder /.venv /.venv

EXPOSE ${PORT}
# Install application into container
COPY fastapi_todos  fastapi_todos/
COPY start.sh .
RUN chmod +x ./start.sh
COPY gunicorn.conf.py .
USER appuser

CMD ["./start.sh"]