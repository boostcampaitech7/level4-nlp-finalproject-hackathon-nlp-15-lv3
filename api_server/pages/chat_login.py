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

st.title("Login")

def check_password():
    """Returns 'True' if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", key="password", type="password")
            a=st.form_submit_button("Log in")#, on_click=password_entered)
            #b=st.form_submit_button("Join")#, on_click=join_form)

            if a:
                click_login()
                if st.session_state["password_correct"]:
                    st.session_state["user_name"] = st.session_state["username"]
                    switch_page("chat")
                
    def join_form():
        with st.form("Join_Form"):
            b=st.form_submit_button("Join")#, on_click=join_form)

            if b:
                click_join()


    def click_join():
        #st.session_state['page'] = 'chat_join.py'
        switch_page("chat_join")

    def click_login():
        '''
        def password_entered():
            """Checks whether a password entered by the user is correct."""
            if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(st.session_state["password"], st.secrets.passwords[st.session_state["username"]],):
                st.session_state["password_correct"] = True
                del st.session_state["password"] # Don't store the username or password
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        '''

        conn = sqlite.connect("./test.db")
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM UserTable WHERE username = '{st.session_state['username']}' AND password = '{st.session_state['password']}';")
        username = cursor.fetchone()

        if username is None:
            st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            #del st.session_state["username"]
        
    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    join_form()

    if "password_correct" in st.session_state:
        st.error("Username or password incorrect")

    return False
    
if not check_password():
    st.stop()

if st.session_state["password_correct"]:
    switch_page("chat")