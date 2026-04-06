from collections import defaultdict
import glob
import os
import sqlparse

from pathlib import Path
from sqlalchemy import MetaData, create_engine, text
from sqlmodel import Session
# from sqlmodel import create_engine, Session

import core.setting as setting

from fastapi.security import OAuth2PasswordBearer
from inspect import isgeneratorfunction
from core.logger import log, log_sql, log_rows, log_except


#
class Database:
    #
    def __init__(self, url: str):
        #
        self.metadata = MetaData()
        self.engine: Session = create_engine(url, echo=False, connect_args={"check_same_thread": False})
        # self.session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)
        self._register_events()
    #
    def get_engine(self):
        #
        return self.engine
    #
    def _register_events(self):
        #
        import time
        from sqlalchemy import event
        #
        @event.listens_for(self.engine, "before_cursor_execute")
        def before_execute(conn, cursor, statement, parameters, context, excutemany):
            #
            if "PRAGMA" in statement:
                return
            #
            explain_cursor = conn.connection.cursor()
            try:
                explain_statement = f"EXPLAIN QUERY PLAN {statement}"
                explain_cursor.execute(explain_statement, parameters)
                plan = explain_cursor.fetchall()
                if plan:
                    log(plan, level='INFO', console=False)
            #
            except Exception as e:
                #
                log_except(e, level='ERROR', console=False)
            #
            finally:
                explain_cursor.close()
            #
            conn.info.setdefault("start_time", []).append(time.time())
        #
        @event.listens_for(self.engine, "after_cursor_execute")
        def after_execution(conn, cursor, statement, parameters, context, excutemany):
            #
            if "PRAGMA" in statement:
                return
            #
            total = time.time() - conn.info["start_time"].pop(-1)
            sql = sqlparse.format(str(statement), reindent=True, keyword_case='upper')
            log_sql(sql, parameters=parameters, porcess_time=total, context=context, level='INFO')
            #
            log_cursor = conn.connection.cursor()
            try:
                if statement.strip().upper().startswith("SELECT"):
                    log_cursor.execute(statement, parameters)
                    rows = log_cursor.fetchall()
                    log_rows(rows)
            #
            except Exception as e:
                #
                log_except(e, level='ERROR', console=False)
            #
            finally:
                log_cursor.close()


#
metadata = None
db = None
engine = None
session = None
oauth2_scheme = None
queries = {}

#
def init():
    #    
    global metadata
    global db
    global engine
    global oauth2_scheme
    #
    settings = setting.settings
    settings.DATABASE_URL = f"sqlite:///{settings.DATABASE_DIR}/{settings.DATABASE_NAME}"
    database = Database(settings.DATABASE_URL)
    #
    db = database
    engine = database.engine
    metadata = database.metadata
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    #
    load_queries()


#
def get_metadata():
    #
    global metadata
    return metadata

#
def get_engine():
    #
    global engine
    return engine

#
def get_db():
    #
    global db
    with Session(db.get_engine()) as session:
        yield session

#
def get_session():
    #
    if isgeneratorfunction(get_db):
        gen = get_db()
        session = next(gen)
    else:
        session = get_db()
    #
    return session

#
def load_initial_data():
    #
    path = "oarcle_initial_data.sql"
    if os.path.exists(path):
        with open(path, "r") as f:
            sql_script = f.read()
        #
        with get_engine().begin() as conn:
            dbapi_conn = conn.connection
            dbapi_conn.executescript(sql_script)

#
def load_queries():
    #
    global queries
    dirs = [x for x in Path('./sql').rglob('*') if x.is_dir()]
    for dir in dirs:
        #
        sql_files = glob.glob(f"{dir}/*.sql")
        for path in sql_files:
            # print(dir)
            # print(path)
            schema = dir.stem
            query_file = Path(path).stem
            #
            if schema not in queries:
                queries[schema] = {}
            #
            if query_file not in queries[schema]:
                #
                with open(path, 'r', encoding='utf-8') as file:
                    query = file.read()
                    queries[schema][query_file] = query
                    #
                    # print(schema)
                    # print(query_file)
                    # print(query)

#
def get_sql(schema, query, params={}):
    #
    global queries
    query_str: str = queries[schema][query]
    query_str = query_str.format_map(params)
    return query_str



# old version, not using custom db wrapper
#
# engine = None
# oauth2_scheme = None
# SessionLocal = None
#
# def init():
#     #
#     global engine
#     global oauth2_scheme
#     global SessionLocal
#     #
#     settings = st.settings
#     settings.DATABASE_URL = f"sqlite:///{settings.DATABASE_DIR}/{settings.DATABASE_NAME}"
#     engine = create_engine(settings.DATABASE_URL, echo=True, connect_args={"check_same_thread": False})
#     oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#     SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
#    
# def get_db():
#     with Session(engine) as session:
#         yield session

