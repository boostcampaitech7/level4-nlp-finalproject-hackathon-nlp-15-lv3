"""
본 파일은 채팅 서버를 구현하는 파일입니다.
https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
위 링크에서 제공하는 채팅 인터페이스를 기반으로 API를 연결하여 채팅 서버를 구현합니다.
"""
import os
from typing import List, Dict, Any
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stateful_button import button
from streamlit_extras.stylable_container import stylable_container
from streamlit_float import *

import requests
import argparse

import sqlite3 as sqlite


st.set_page_config(layout='wide')

html_code = """
            <script>
            
            function sc(){
                window.onload = function() {
                window.scrollTo(0, stChatMessage.scrollHeight);
                };
            }
            </script>
            """
components.html(html_code, height=0)

question = ""

float_init()

#col1, _, col2, col3, col4 = st.columns(5)
_, col3, col4 = st.columns([10, 1, 1])
col3.float()
col4.float()

if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
    st.session_state["password_correct"] = False
    st.session_state["history"] = []

if st.session_state["user_name"]:
    a = col4.button("Log out")
    if a:
        st.session_state["user_name"] = ""
        st.session_state["password_correct"] = False
        st.session_state["history"] = []
        switch_page("chat")

else:
    a = col3.button("Log in")
    b = col4.button("Join")
    
    if a:
        switch_page("chat_login")
    if b:
        switch_page("chat_join")



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

def scroll_bottom():
    html_code = f"""
                <script>
                sc();
                </script>
                """
    components.html(html_code, height=0)
    
def logging(messages):

    # db conn
    # db write
    # db close?

    conn = sqlite.connect("./test.db")
    cursor = conn.cursor()

    for message in messages:
        #cursor.execute(f"INSERT INTO ChatTable VALUES ('{st.session_state['user_name']}', datetime('now'), '{message['role']}', '{message['content']}');")
        cursor.execute("INSERT INTO ChatTable VALUES (?, datetime('now'), ?, ?)", (st.session_state['user_name'], message['role'], message['content']))
    conn.commit()

def chat(args: argparse.Namespace) -> None:
    """
    채팅을 구현합니다.
    :param args:
    :return:
    """

    #global prompt, do_web_search, response
    #global question

    # Title
    #st.title(args.title)
    st.markdown("<h1 style='text-align: center;'>RAG CHAT DEMO</h1>", unsafe_allow_html=True)


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
    #with st.container():
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if st.get_option("theme.base") == "light":
        background_color = "white"
        text_color = "black"
    else:
        background_color = "#0E1117"
        text_color = "white"

    st.markdown(f"""
        <style>
        .fixed-bottom {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: {background_color};
            color: {text_color};
            padding: 45px;
            box-shadow: 0 0px 0px rgba(0,0,0,0);
            display: flex;
            justify-content: space-between;
            z-index: 9998;
        }}
        </style>
    """, unsafe_allow_html=True)


    # Create a div container at the bottom
    st.markdown('<div class="fixed-bottom" id="fixed_bottom"></div>', unsafe_allow_html=True)
    
    # 세션 상태에 선택된 질문이 없으면 초기화
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = ""

    prompt = ""
    do_web_search = False

    with stylable_container(
            key="chat_input_container",
            css_styles="""
                {
                    position: fixed;
                    bottom: 50px;
                    z-index: 9999;
                }
                """,
        ):
        col1, col2 = st.columns([1,11])
        #do_web_search = col1.button("Web Search")
        with col1:
            do_web_search = button("Web Search", key="web_search_button")
        
        prompt = col2.chat_input("Type here!")
        
        if st.session_state.selected_question:
            prompt = st.session_state.selected_question
            st.session_state.selected_question = ""
        
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chatbot response
        response = ""

        cont = st.empty()
        with cont.container():
            with st.status("Answering...", expanded=False):
                if do_web_search:
                    response = request_api(st.session_state.messages, args.server_api+"/chat_web/chat_web")
                else:
                    response = request_api(st.session_state.messages, args.chat_api)
        cont.empty()

        with st.chat_message("assistant"):
            response = st.write_stream(stream_generator(response))

        # Add chatbot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        if "user_name" in st.session_state:# and st.session_state["user_name"]:
            logging(st.session_state.messages)


        scroll_bottom()


        #st.write("추천 질문:")

        def update_question():
            st.session_state.selected_question = st.session_state.radio_question

        cont = st.empty()
        with cont.container():
            with st.status("Recommended questions:", expanded=True):
                response = request_api(st.session_state.messages, args.server_api+"/recommend")
        

                #st.write_stream(stream_generator(response))
                questions = stream_to_string(response).strip().split("@")[1:]
                
                st.session_state.questions = questions
                st.session_state.selected_question = st.radio(
                    "추천 질문:",
                    st.session_state.questions,
                    index=None,
                    key="radio_question",
                    on_change=update_question,
                    label_visibility="hidden",
                )
        
        if st.session_state.selected_question:
            cont.empty()
            #del st.session_state.questions
        #else:
        #    st.rerun()

def stream_generator(response):
    for i,chunk in enumerate(response):
        #if i%10==0:scroll_bottom()
        yield chunk.decode("utf-8")

def stream_to_string(response):
    res = ""
    for i,chunk in enumerate(response):
        res += chunk.decode("utf-8")
    return res

def settings():
    st.title("Settings")
    st.write("This is the settings page.")


def main(args: argparse.Namespace) -> None:
    chat(args)

if __name__ == "__main__":

    if "db_exists" not in st.session_state:
        #conn = sqlite3.connect(':memory:') # for in-memory
        conn = sqlite.connect('./test.db') # for persistent file
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS ChatTable (username VARCHAR(16), datetime TIMESTAMPTZ, role text, chat text);")
        cur.execute("INSERT INTO ChatTable Values ('test', datetime('now'), 'user', 'test');")

        cur.execute("CREATE TABLE IF NOT EXISTS UserTable (username VARCHAR(16), password VARCHAR(32));")
        cur.execute("INSERT INTO UserTable VALUES ('test', 'test');")

        conn.commit()
        cur.close()
        conn.close()
        st.session_state["db_exists"] = True

    parser = argparse.ArgumentParser()
    parser.add_argument("--server_api", type=str, default="http://localhost:30002/")
    parser.add_argument("--chat_api", type=str, default="http://localhost:30002/chat")
    parser.add_argument("--title", type=str, default="RAG Chatbot Demo")
    main(parser.parse_args())

