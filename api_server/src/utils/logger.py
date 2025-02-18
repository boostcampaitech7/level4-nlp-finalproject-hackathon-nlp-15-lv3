import logging
from typing import Optional

def setup_logger(
    level: int = logging.INFO,
    format: str = '%(asctime)s - %(levelname)s - %(message)s',
    datefmt: str = '%Y-%m-%d %H:%M:%S',
    watchfiles_level: int = logging.WARNING
) -> logging.Logger:
    """애플리케이션 전역 로거 설정"""
    
    # 로깅 포맷터 설정
    formatter = logging.Formatter(
        format,
        datefmt=datefmt
    )

    # Root 로거 설정
    logger = logging.getLogger()
    logger.setLevel(level)

    # 핸들러 설정
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # watchfiles 로거 레벨 조정
    logging.getLogger('watchfiles.main').setLevel(watchfiles_level)

    return logger