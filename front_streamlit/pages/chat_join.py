"""
본 파일은 채팅 서버를 구현하는 파일입니다.
https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
위 링크에서 제공하는 채팅 인터페이스를 기반으로 API를 연결하여 채팅 서버를 구현합니다.
"""
import os
from typing import List, Dict, Any
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import hmac
import requests
import argparse

import psycopg2
from psycopg2.extras import RealDictCursor

import sqlite3 as sqlite

st.title("Join")

def join():
    """Returns 'True' if all done"""

    def join_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", key="password", type="password")
            check = st.form_submit_button("Complete")#, on_click=join_db)
            return check
    
    def join_check():
        check = True
        err = "E0"
        
        if not (st.session_state['username'] and st.session_state['password']):
            check, err = False, "Fill the information."
        elif user_check(): # later change to db
            check, err = False, "The username already exists."

        if not check:
            st.error(err)

        return check
        
    def user_check():
        conn = sqlite.connect("./test.db")
        cursor = conn.cursor()

        print(st.session_state['username'])
        cursor.execute(f"SELECT * FROM UserTable WHERE username = '{st.session_state['username']}';")
        username = cursor.fetchone()

        print(username)

        if username:
            return True
        else:
            return False

    def join_db():
        """Checks whether a password entered by the user is correct."""
        conn = sqlite.connect("./test.db")
        cursor = conn.cursor()

        cursor.execute(f"INSERT INTO UserTable VALUES ('{st.session_state['username']}', '{st.session_state['password']}');")
    
        conn.commit()
        cursor.close()
        conn.close()

    # Show inputs for username + password.
    if join_form():
        if join_check():
            join_db()
            return True

    return False

if not join():
    st.stop()
else:
    switch_page("chat_login")
