import json
import multiprocessing
import os

# The suggested number of workers is (2*CPU)+1
# The maximum concurrent requests areworkers * threads 10 in our case.
# The suggested maximum concurrent requests when using workers and threads is still(2*CPU)+1

workers_per_core_str = os.getenv("WORKERS_PER_CORE", os.getenv("CPUS", "3"))
max_workers_str = os.getenv("MAX_WORKERS", None)
use_max_workers = None

# CPU Requests & Limits
cores_min = 2
cores_max = 4
try:
    # Case 1: cpu: "2"
    cores_min = max(1, int(os.getenv("CPU_MIN", "1")))
except ValueError:
    # Case 2: cpu: "150m"
    cores_min_mili = os.getenv("CPU_MIN")
    cores_min = max(1, int(cores_min_mili.split("m")[0]) / 1000)
except Exception:
    # Case 3: use 1 as default
    cores_min = 1

try:
    # Case 1: cpu: "2"
    cores_max = max(1, int(os.getenv("CPU_MAX", "1")))
except ValueError:
    # Case 2: cpu: "150m"
    cores_max_mili = os.getenv("CPU_MAX")
    cores_max = max(1, int(cores_max_mili.split("m")[0]) / 1000)
except Exception:
    # Case 3: use 1 as default
    cores_max = 1

cores = max(cores_min, cores_max)

if max_workers_str:
    use_max_workers = int(max_workers_str)
else:
    use_max_workers = int(workers_per_core_str) * cores
use_threads = int(os.getenv("THREADS", cores * 3))
# use_threads = int(os.getenv("THREADS", "4"))
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = max(int(web_concurrency_str), 2)
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if use_max_workers:
        web_concurrency = min(web_concurrency, use_max_workers)


host = os.getenv("APP_HOST", "0.0.0.0")
port = os.getenv("APP_PORT", "8000")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

accesslog_var = os.getenv("ACCESS_LOG", "-")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("ERROR_LOG", "-")
use_errorlog = errorlog_var or None
graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "60")
timeout_str = os.getenv("TIMEOUT", "60")
keepalive_str = os.getenv("KEEP_ALIVE", "60")


# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
threads = use_threads
bind = use_bind
errorlog = use_errorlog
# worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
# '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
# access_log_format='%(asctime)s.%(msecs)03d %(levelname)-5s %(process)5d --- [%(funcName)30s] %(name)-40s : %(message)s'
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)


# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "use_max_workers": use_max_workers,
    "host": host,
    "port": port,
}

print(json.dumps(log_data))
