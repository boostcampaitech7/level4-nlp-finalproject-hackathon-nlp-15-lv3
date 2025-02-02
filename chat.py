"""
본 파일은 채팅 서버를 구현하는 파일입니다.
https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
위 링크에서 제공하는 채팅 인터페이스를 기반으로 API를 연결하여 채팅 서버를 구현합니다.
"""
from typing import List, Dict, Any
import streamlit as st
import requests
import argparse


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


def chat(args: argparse.Namespace) -> None:
    """
    채팅을 구현합니다.
    :param args:
    :return:
    """

    st.title(args.title)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
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


def settings():
    st.title("Settings")
    st.write("This is the settings page.")


def main(args: argparse.Namespace) -> None:
    chat(args)
    with st.sidebar:
        settings()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_api", type=str, default="http://localhost:8000/chat")
    parser.add_argument("--title", type=str, default="RAG Chatbot Demo")
    main(parser.parse_args())

