import streamlit as st


# to make your app take up all the available space in the browser window
# (not just a single column)
st.set_page_config(layout='wide')

col1, col2, col3, col4 = st.columns(4)

# this will put a button in the middle column
col1.button("wh10")
with col2:
    st.button("I 1am a button")
col3.button("ff1")
col4.button("Lo1 out")



st.title("Title of an app")

# you can create columns to better manage the flow of your page
# this command makes 3 columns of equal width
col1, col2, col3, col4 = st.columns(4)

# this will put a button in the middle column
col1.button("wh0")
with col2:
    st.button("I am a button")
col3.button("ff")
col4.button("Log out")

st.write("Now on to the other columns")

# this command will make 3 columns of unequal width
# first column is largest and 3x the size of the last,
# second column is 2x the size of the last
col4, col5, col6 = st.columns([3,2,1])

# this will put a checkbox in the last column
col4.checkbox("test")
col5.text_input("ttt")
col6.checkbox("I am a checkbox")

col4, col5, col6 = st.columns([3,2,1])

# this will put a checkbox in the last column
col4.text_input("tes2t")
col5.text_input("tt2t")
col6.text_input("I a2m a checkbox")






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

import sqlite3 as sqlite

#st.title("chat")

def request_api(messages: List[Dict[str, Any]], url: str):
    """
    API 서버로부터 응답을 받아옵니다.
    Args:
        messages: List[Dict[str, Any]]: 사용자의 메시지 목록.
            - role: str: 사용자의 역할.
            - content: str: 사용자의 메시지 내용.
    Returns:
        List[Dict[str, Any]]: 챗봇의 응답 메시지 목록.
            - role: str: 챗봇의 역할.
            - content: str: 챗봇의 메시지 내용.
    """
    data = {
        "id": "test",
        "name": "test",
        "group_id": "test",
        "messages": messages,
        "max_query_size": 1024,
        "max_response_size": 4096,
        "top_k": 3,
        "stream": True
    }

    response = requests.post(url, json=data, stream=True)
    return response


def logging(messages):

    # db conn
    # db write
    # db close?

    conn = sqlite.connect("./test.db")
    cursor = conn.cursor()

    for message in messages:
        cursor.execute(f"INSERT INTO ChatTable VALUES ('{st.session_state['user_name']}', datetime('now'), '{message['role']}', '{message['content']}');")
    conn.commit()

def chat(args: argparse.Namespace) -> None:
    """
    채팅을 구현합니다.
    :param args:
    :return:
    """

    st.title(args.title)

    # Initialize chat history
    #print("st state",st.session_state)
    #if "messages" not in st.session_state:
    #    st.session_state.messages = []

    st.session_state.history = []
    st.session_state.messages = []

    if "history" in st.session_state:#else:
        conn = sqlite.connect("./test.db")
        cursor = conn.cursor()

        if "user_name" in st.session_state:
            try:
                cursor.execute(f"SELECT * FROM ChatTable WHERE username = '{st.session_state['user_name']}';")
                table = cursor.fetchall()
                #print(table)
            
                columns = [d[0] for d in cursor.description]
                #print(table, columns)
                for row in table:
                    role=""
                    content=""
                    for column, value in zip(columns, row):
                        if column=="role":role=value
                        elif column=="chat":content=value
                    st.session_state.history += [{"role":role, "content":content}]
            except Exception as e:
                print("[chat.py] SELECT failed", e)

    # Display chat messages from history on app rerun

    #print(st.session_state)
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Type here"):
        # Add user message to chat history
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chatbot response
        response = request_api(st.session_state.messages, args.chat_api)
        def _genertor():
            for chunk in response:
                yield chunk.decode("utf-8")

        with st.chat_message("assistant"):
            response = st.write_stream(_genertor())

        # Add chatbot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        if "user_name" in st.session_state:
            logging(st.session_state.messages)

def settings():
    st.title("Settings")
    st.write("This is the settings page.")


def main(args: argparse.Namespace) -> None:
    chat(args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_api", type=str, default="http://localhost:8000/chat")
    parser.add_argument("--title", type=str, default="RAG Chatbot Demo")
    main(parser.parse_args())







'''
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        .block-container {padding-bottom: 0 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([5, 3])

with col1:
    st.title("Some cute cat")
    st.slider("Select hour of pickup")
    st.image("https://static.streamlit.io/examples/cat.jpg", width=300)

with col2:
    st.markdown("Some text and a cute picture of a dog")
    st.image("https://static.streamlit.io/examples/dog.jpg")

with st.container():
    st.markdown("Here is a container")
'''