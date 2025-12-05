"""
통합 로깅 시스템
- 구조화된 로그
- 로그 레벨 관리
- 파일 로테이션
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 추가 컨텍스트 정보
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # 예외 정보
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """컬러 로그 포매터 (콘솔용)"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_dir: str = "logs",
    log_level: str = "INFO",
    enable_json: bool = True,
    enable_console: bool = True
) -> logging.Logger:
    """로깅 시스템 초기화"""
    
    # 로그 디렉토리 생성
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거
    root_logger.handlers.clear()
    
    # 파일 핸들러 (JSON 형식)
    if enable_json:
        json_handler = RotatingFileHandler(
            log_path / "app.json.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        json_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(json_handler)
    
    # 파일 핸들러 (일반 텍스트)
    text_handler = TimedRotatingFileHandler(
        log_path / "app.log",
        when="midnight",
        interval=1,
        backupCount=30
    )
    text_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    text_handler.setFormatter(text_formatter)
    root_logger.addHandler(text_handler)
    
    # 콘솔 핸들러
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 에러 전용 파일 핸들러
    error_handler = RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(text_formatter)
    root_logger.addHandler(error_handler)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """이름 기반 로거 생성"""
    return logging.getLogger(name)


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """컨텍스트 정보와 함께 로그 기록"""
    log_func = getattr(logger, level.lower())
    log_func(message, extra={"context": context or {}})


# API 요청/응답 로깅
class RequestLogger:
    """API 요청/응답 로거"""
    
    def __init__(self):
        self.logger = get_logger("api.requests")
    
    def log_request(
        self,
        method: str,
        path: str,
        client_ip: str,
        user_agent: Optional[str] = None
    ):
        """요청 로그"""
        self.logger.info(
            f"{method} {path}",
            extra={
                "context": {
                    "method": method,
                    "path": path,
                    "client_ip": client_ip,
                    "user_agent": user_agent
                }
            }
        )
    
    def log_response(
        self,
        method: str,
        path: str,
        status_code: int,
        response_time: float
    ):
        """응답 로그"""
        level = "info" if status_code < 400 else "error"
        getattr(self.logger, level)(
            f"{method} {path} - {status_code} ({response_time:.3f}s)",
            extra={
                "context": {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "response_time": response_time
                }
            }
        )


# 전역 인스턴스
request_logger = RequestLogger()


# 성능 로깅
class PerformanceLogger:
    """성능 메트릭 로거"""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_slow_query(self, query: str, duration: float, threshold: float = 1.0):
        """느린 쿼리 로그"""
        if duration > threshold:
            self.logger.warning(
                f"Slow query detected: {duration:.3f}s",
                extra={
                    "context": {
                        "query": query[:200],
                        "duration": duration,
                        "threshold": threshold
                    }
                }
            )
    
    def log_cache_stats(self, stats: Dict[str, Any]):
        """캐시 통계 로그"""
        self.logger.info(
            "Cache statistics",
            extra={"context": stats}
        )
    
    def log_api_performance(self, endpoint: str, metrics: Dict[str, Any]):
        """API 성능 로그"""
        self.logger.info(
            f"API performance: {endpoint}",
            extra={"context": metrics}
        )


# 전역 인스턴스
performance_logger = PerformanceLogger()
