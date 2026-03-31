
import json
import logging
import logging.handlers
import os
import pandas as pd
import traceback

from datetime import datetime
from starlette.responses import Response, StreamingResponse, JSONResponse

import core.setting as setting


logger = None
log_level_limit = 0


def init():
    
    global logger

    settings = setting.settings
    
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine.Engine').disabled = True
    logging.getLogger("sqlalchemy").handlers = [logging.NullHandler()]

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # console_handler = logging.StreamHandler()
    # logger.addHandler(info_handler)

    debug_handler = logging.handlers.TimedRotatingFileHandler(
        filename = os.path.join(settings.LOG_DIR, 'debug.log'), 
        backupCount=50,
        when='M',
        interval=1,
    )
    debug_handler.setLevel(logging.DEBUG) 
    logger.addHandler(debug_handler)

    info_handler = logging.handlers.TimedRotatingFileHandler(
        filename = os.path.join(settings.LOG_DIR, 'info.log'), 
        backupCount=10,
        when='H',
        interval=1,
        encoding="utf-8",
    )
    info_handler.setLevel(logging.INFO) 
    logger.addHandler(info_handler)

    warn_handler = logging.handlers.TimedRotatingFileHandler(
        filename = os.path.join(settings.LOG_DIR, 'warn.log'), 
        backupCount=20,
        when='H',
        interval=1,
        encoding="utf-8",
    )
    warn_handler.setLevel(logging.WARNING) 
    logger.addHandler(warn_handler)

    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename = os.path.join(settings.LOG_DIR, 'error.log'), 
        backupCount=30,
        when='H',
        interval=1,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR) 
    logger.addHandler(error_handler)

    critical_handler = logging.handlers.TimedRotatingFileHandler(
        filename = os.path.join(settings.LOG_DIR, 'critical.log'), 
        backupCount=40,
        when='H',
        interval=1,
        encoding="utf-8",
    )
    critical_handler.setLevel(logging.CRITICAL) 
    logger.addHandler(critical_handler)

    # bocking porint
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)


def int_log_level(level):
    # default: error
    log_level = 3 
    #
    log_levels = ['debug', 'info', 'warn', 'error', 'critical']
    if level in log_levels:
        log_level = log_levels.index(level)
    #
    log_levels = ['Debug', 'Info', 'Warn', 'Error', 'Critical']
    if level in log_levels:
        log_level = log_levels.index(level)
    #
    log_levels = ['DEBUG', 'INFO', 'WARN', 'ERRIR', 'CRITICAL']
    if level in log_levels:
        log_level = log_levels.index(level)
    #
    return log_level


def write_log(log_level: int, log :str, console=True):
    #
    if log_level == 0:
        logging.debug(log)
    #
    if log_level == 1:
        logging.info(log)
    #
    if log_level == 2:
        logging.warning(log)
    #
    if log_level == 3:
        logging.error(log)
    #
    if log_level == 4:
        logging.critical(log)
    #
    if console:
        print(log)


def log(message, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    log_format = f'''
---------------------------------------------------------------------------------------------   
Log
---------------------------------------------------------------------------------------------   
log level: \t {log_level}
timestamp: \t {timestamp}
message: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{message}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)


def log_except(message, level='ERROR', console=True):
    #
    global log_level_limit
    #
    
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    err_msg = traceback.format_exc()
    #
    log_format = f'''
---------------------------------------------------------------------------------------------   
Exception
---------------------------------------------------------------------------------------------   
log level: \t {log_level}
timestamp: \t {timestamp}
message: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{message}
{err_msg}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)



def log_sql(sql, parameters, porcess_time=0, context=None, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    if "PRAGMA" in sql:
        return
    #
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    if parameters:
        for param in parameters:
            sql = sql.replace('?', f"'{param}'", 1)
    #
    log_format = f'''
---------------------------------------------------------------------------------------------
SQL
---------------------------------------------------------------------------------------------
log level: \t {log_level}
timestamp: \t {timestamp}
time: \t {porcess_time}
sql: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{sql}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)


def log_rows(rows, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    formatted_rows = ["\t| ".join([str(c) for c in row]) for row in rows]
    str_rows = "\n-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -\n".join(formatted_rows)
    #
    log_format = f'''
---------------------------------------------------------------------------------------------
SQL Rows
---------------------------------------------------------------------------------------------   
log level: \t {log_level}
rows: {len(rows)}
sql: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{str_rows}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)


#
def log_df(df, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    log_format = f'''
---------------------------------------------------------------------------------------------
Dataframe
---------------------------------------------------------------------------------------------   
log level: \t {log_level}
rows: {len(df)}
sql: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{df.to_string()}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)


#
def log_response(target, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    if not isinstance(target, JSONResponse):
        return
    #
    message = target.body.decode('utf-8')
    message_dict = json.loads(message)
    message = json.dumps(message_dict, indent=4, sort_keys=True)
    err_msg = traceback.format_exc()
    log_format = f'''
---------------------------------------------------------------------------------------------   
Response
---------------------------------------------------------------------------------------------
log level: \t {log_level}
timestamp: \t {timestamp}
response: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{message}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
{err_msg}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)


def log_dict(data, level='INFO', console=True):
    #
    global log_level_limit
    #
    log_level = int_log_level(level)
    if log_level_limit > log_level:
        return
    #
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #
    if not isinstance(data, dict):
        return 
    #
    message = json.dumps(data, indent=4, ensure_ascii=False)   
    log_format = f'''
---------------------------------------------------------------------------------------------   
Dictionary
---------------------------------------------------------------------------------------------
log level: \t {log_level}
timestamp: \t {timestamp}
response: 
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
{message}
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    '''
    #
    write_log(log_level=log_level, log=log_format, console=console)
