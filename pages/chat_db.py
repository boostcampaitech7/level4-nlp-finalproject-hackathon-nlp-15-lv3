"""
본 파일은 채팅 서버를 구현하는 파일입니다.
https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
위 링크에서 제공하는 채팅 인터페이스를 기반으로 API를 연결하여 채팅 서버를 구현합니다.
"""
import os
from typing import List, Dict, Any
import streamlit as st
import requests
import argparse

import psycopg2
from psycopg2.extras import RealDictCursor

import sqlite3 as sqlite


st.title("sqlite3 DB test")

#conn = sqlite3.connect(':memory:') # for in-memory
conn = sqlite.connect('./test.db') # for persistent file
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS ChatTable (username VARCHAR(16), datetime TIMESTAMPTZ, role text, chat text);")
cur.execute("INSERT INTO ChatTable Values ('test', datetime('now'), 'user', 'test');")

cur.execute("CREATE TABLE IF NOT EXISTS UserTable (username VARCHAR(16), password VARCHAR(32));")
cur.execute("INSERT INTO UserTable VALUES ('test', 'test');")

cur.execute("SELECT * FROM UserTable;")
table = cur.fetchall()

for row in table:
    s=''
    for v in row:
        if type(v) is not str:v=str(v)
        s+=v+' '
    st.write(s)

conn.commit()
cur.close()
conn.close()