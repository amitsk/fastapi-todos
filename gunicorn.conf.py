# https://docs.gunicorn.org/en/latest/configure.html
# https://docs.gunicorn.org/en/latest/settings.html#settings

import json
import multiprocessing
import os

workers_per_core_str = os.environ.get("WORKERS_PER_CORE", "2")
# https://docs.gunicorn.org/en/latest/settings.html#bind
port = os.environ.get("PORT", "8000")
use_loglevel = os.environ.get("LOG_LEVEL", "info")

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
workers = int(workers_per_core * cores)

accesslog_var = os.environ.get("ACCESS_LOG")
use_accesslog = accesslog_var or None
errorlog_var = os.environ.get("ERROR_LOG", "-")
use_errorlog = errorlog_var or None
graceful_timeout_str = os.environ.get("GRACEFUL_TIMEOUT", "120")
timeout_str = os.environ.get("TIMEOUT", "120")
keepalive_str = os.environ.get("KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = use_loglevel
errorlog = use_errorlog
# https://docs.gunicorn.org/en/latest/faq.html#blocking-os-fchmod
worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)


# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "port": port,
}
print(json.dumps(log_data))