import sqlite3
from . import sqlutils
from typing import List, Callable
from ...generic.utils import data, parse_time
import logging
import time
import threading
sql_logger = logging.getLogger("sqlite3")
timer = None
@sqlutils.handleSQLErrors
def start_signups(conn: sqlite3.Connection, t: int):
    sql_logger.debug("Starting signups with deadline in {:d} ms".format(t))
    sqlutils.setPhase(conn, "signups")
    sqlutils.setDeadline(conn, t)
    sqlutils.setStartTime(conn, time.time_ns() // 1000000)

@sqlutils.handleSQLErrors
def start_responding(conn: sqlite3.Connection, defaultResponseCount: int, t: int, prompt: str):
    if defaultResponseCount is None: defaultResponseCount = 1
    sqlutils.setPhase(conn, "responding")
    sqlutils.setPrompt(conn, prompt)
    sqlutils.setStartTime(conn, time.time_ns())
    sqlutils.setDeadline(conn, t)
    sqlutils.wipeAllResponses(conn)
    sqlutils.setAllResponseCount(conn, defaultResponseCount)

@sqlutils.handleSQLErrors
def end_responding(conn: sqlite3.Connection):
    contestants = sqlutils.getAllContestants(conn)
    for contestant in contestants:
        if contestant["responseCount"] == 0:
            sqlutils.killContestant(conn, contestant["uid"])

@sqlutils.handleSQLErrors
def fixTime(conn: sqlite3.Connection):
    deadline = sqlutils.getDeadline(conn)
    stime = sqlutils.getTime(conn)
    ctime = time.time_ns() // 1000000
    deadline -= ctime - stime
    phase = sqlutils.phase(conn)
    if deadline <= 0: 
        if phase == "responding":
            end_responding(conn)
        elif phase == "signups":
            end_signups(conn)
        elif phase == "voting":
            end_voting(conn)
    else:
        sqlutils.setDeadline(conn, deadline)
        sqlutils.setStartTime(conn, ctime)

@sqlutils.handleSQLErrors
def start_voting(conn):
    pass

@sqlutils.handleSQLErrors
def end_voting(conn: sqlite3.Connection):
    pass

@sqlutils.handleSQLErrors
def end_signups(conn: sqlite3.Connection):
    pass

def setTimer(ms: int, func: Callable, *args, **kwargs):
    timer = threading.Timer(ms / 1000, func, *args, **kwargs)
    timer.start()

def stopTimer():
    if timer is not None:
        timer.cancel()