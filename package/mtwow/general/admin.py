import sqlite3
from . import sqlutils
from typing import List, Callable
from ...generic.utils import data, parse_time
import logging
import time
sql_logger = logging.getLogger("sqlite3")

def setPhase(conn: sqlite3.Connection, status: str):
    sql_logger.debug("Set phase to {:s}".format(status))
    conn.execute("UPDATE Status SET phase=?;", (status,))

def setDeadline(conn: sqlite3.Connection, time: int):
    sql_logger.debug("Set deadline to {:d}ms after now.".format(time))
    conn.execute("UPDATE Status SET deadline=?;", (time,))

def setStartTime(conn: sqlite3.Connection, time: int):
    sql_logger.debug("Set time phase started to {:d}ms after epoch.".format(time))
    conn.execute("UPDATE Status SET startTime=?;", (time,))

def setPrompt(conn: sqlite3.Connection, prompt: str):
    sql_logger.debug("Set prompt to:\n{:s}".format(prompt))
    conn.execute("UPDATE Status SET prompt=?;", (prompt,))

def setAllResponseCount(conn: sqlite3.Connection, count: int):
    sql_logger.debug("Set default response count to {:d}".format(count))
    conn.execute("UPDATE Contestants SET allowedResponses = 1;")

def wipeAllResponses(conn: sqlite3.Connection):
    sql_logger.warning("Wiping all responses!")
    conn.execute("DELETE FROM Responses;")

@sqlutils.handleSQLErrors
def start_signups(conn: sqlite3.Connection, t: int):
    sql_logger.debug("Starting signups with deadline in {:d} ms".format(t))
    setPhase(conn, "signups")
    setDeadline(conn, t)
    setStartTime(conn, time.time_ns() // 1000000)

@sqlutils.handleSQLErrors
def start_responding(conn: sqlite3.Connection, defaultResponseCount: int, t: int, prompt: str):
    if defaultResponseCount is None: defaultResponseCount = 1
    setPhase(conn, "responding")
    setPrompt(conn, prompt)
    setStartTime(conn, time.time_ns())
    setDeadline(conn, t)
    wipeAllResponses(conn)
    setAllResponseCount(conn, defaultResponseCount)

