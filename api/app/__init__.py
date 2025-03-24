from logging import INFO, WARNING, Logger, root

from app.px.pxlogger import configure_logger, configure_root_logger

configure_root_logger()
for logger in root.manager.loggerDict.values():
    if not isinstance(logger, Logger):
        continue
    if logger.name in ("uvicorn.access"):
        configure_logger(logger, logging_level=INFO)
    else:
        configure_logger(logger, logging_level=WARNING)
