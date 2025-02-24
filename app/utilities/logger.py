import logging
import sys

logging.basicConfig(
    stream=sys.stdout,
    level=settings.logging_level,
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",  # noqa: E501
    datefmt="%d/%b/%Y %H:%M:%S",
)
logger = logging.getLogger("my-todos")