"""
Gunicorn 설정 파일
Production 환경 최적화 설정
"""

import multiprocessing
import os

# 서버 소켓
bind = "0.0.0.0:8000"
backlog = 2048

# 워커 설정
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# 로깅
accesslog = "/var/log/zerosite/access.log"
errorlog = "/var/log/zerosite/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 프로세스 이름
proc_name = "zerosite_v7"

# 데몬 설정
daemon = False
pidfile = "/var/run/zerosite/zerosite.pid"
user = None
group = None
umask = 0

# 보안
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 서버 메커니즘
preload_app = True
sendfile = True
reuse_port = True

# 워커 라이프사이클 훅
def on_starting(server):
    """서버 시작 시"""
    print(f"Gunicorn starting with {workers} workers")

def when_ready(server):
    """서버 준비 완료 시"""
    print("Gunicorn is ready. Spawning workers")

def on_reload(server):
    """서버 리로드 시"""
    print("Gunicorn reloading")

def worker_int(worker):
    """워커 인터럽트 시"""
    print(f"Worker {worker.pid} received INT or QUIT signal")

def worker_abort(worker):
    """워커 강제 종료 시"""
    print(f"Worker {worker.pid} aborted")

# 환경별 설정 오버라이드
env = os.getenv("ENVIRONMENT", "production")

if env == "development":
    workers = 2
    reload = True
    loglevel = "debug"
elif env == "staging":
    workers = multiprocessing.cpu_count() + 1
    loglevel = "info"
