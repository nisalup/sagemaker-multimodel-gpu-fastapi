#!/usr/bin/env python
"""
Create Nginx/Gunicorn entrypoint for Sagemaker
"""
import os
import signal
import subprocess
import sys

import logging as log

CPU_COUNT = 1  # int(os.cpu_count())
MODEL_SERVER_TIMEOUT = 3600
MODEL_SERVER_WORKERS = CPU_COUNT


def sigterm_handler(nginx_pid: int, gunicorn_pid: int) -> None:
    """Kill nginx and gunicorn processes using SIGTERM.

    Parameters
    ----------
    nginx_pid : int
        process id of nginx
    gunicorn_pid : int
        process id of gunicorn
    """
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass

    sys.exit(0)


def start_server() -> None:
    """Start checkbox_detector Extractor's Nginx/Gunicorn server."""
    log.info(
        f"""
        Starting the inference server with {MODEL_SERVER_WORKERS}
        workers.
        """)

    # link the log streams to stdout/err so they will be logged
    # to the container logs
    subprocess.check_call(
        [
            "ln", "-sf", "/dev/stdout", "/var/log/nginx/access.log"
        ]
    )
    subprocess.check_call(
        [
            "ln", "-sf", "/dev/stderr", "/var/log/nginx/error.log"
        ]
    )

    nginx = subprocess.Popen(["nginx", "-c", "/app/nginx.conf"])
    gunicorn = subprocess.Popen(
        [
            "gunicorn",
            "--timeout",
            str(MODEL_SERVER_TIMEOUT),
            "-k",
            "uvicorn.workers.UvicornWorker",
            "--bind",
            "unix:/tmp/gunicorn.sock",  # Update the socket path
            "sm_multimodel_gpu_fastapi.app:APP",
        ]
    )

    signal.signal(
        signal.SIGTERM,
        lambda a, b: sigterm_handler(
            nginx.pid, gunicorn.pid
        )
    )

    # If either subprocess exits, so do we.
    pids = {nginx.pid, gunicorn.pid}
    while True:
        pid, _ = os.wait()
        if pid in pids:
            break

    sigterm_handler(nginx.pid, gunicorn.pid)
    log.error("Inference server exiting")


# The main routine just invokes the start
# function.


if __name__ == "__main__":
    start_server()
