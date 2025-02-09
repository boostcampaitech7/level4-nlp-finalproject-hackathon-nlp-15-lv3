'use client';

import React, { useState, useMemo } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import {
  CONVERSATION_END,
  HELP_START_OPTIONS,
  createNewAssistantMessage,
  createNewUserMessage,
  firstMessage,
  responseConditions,
  resetMessageIdCounter,
} from '@/utils';
import ChatContext from './ChatContext';

export default function ChatProvider({ children }) {
  const [historicMessages, setHistoricMessages] = useState([]);
  const [messages, setMessages] = useState([firstMessage]);
  const [user, setUser] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isFinishedConversation, setIsFinishedConversation] = useState(false);

  const handleAssistantResponse = (response) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      createNewAssistantMessage(response.content, response.options, response.reference),
    ]);
  };

  const handleFallbackAssistantResponse = () => {
    if (!user) {
      setMessages((prevMessages) => [
        ...prevMessages, createNewAssistantMessage(null, HELP_START_OPTIONS),
      ]);
    } else {
      setMessages((prevMessages) => [...prevMessages, createNewAssistantMessage(null, [{
        id: 1, option: 'Loan', response: 'loan', description: 'Loan',
      }])]);
    }
  };

  const getBotResponse = async (message) => {
    setIsTyping(true);

    // 사용자 메시지 목록 구성
    const payload = {
      id: 'test',
      name: 'test',
      group_id: 'test',
      messages: [
        ...messages,
        { role: 'user', content: message },
      ],
      max_query_size: 1024,
      max_response_size: 4096,
      top_k: 3,
      stream: false,
    };

    try {
      // 새 API 호출
      const response = await axios.post('http://localhost:30002/chat', payload);

      // 2) API에서 반환된 데이터가 [{role: "...", content: "..."}] 형태라고 가정
      const data = response.data; 
      console.log('API Response:', data);
      if (Array.isArray(data)) {
        // 배열 형태라면 여러 메시지를 순회하여 각각 추가
        data.forEach((msg) => {
          if (msg.role === 'assistant') {
            setMessages((prev) => [...prev, createNewAssistantMessage(msg.content)]);
          } else if (msg.role === 'user') {
            setMessages((prev) => [...prev, createNewUserMessage(msg.content)]);
          } else {
            // 필요한 경우 다른 역할도 처리
          }
        });
      } else {
        // 배열이 아닌 경우(단일 객체 등) 처리
        setMessages(prev => [...prev, createNewAssistantMessage(data)]);
      }
    } catch (error) {
      console.error('API Error:', error);
      handleFallbackAssistantResponse();
    } finally {
      setIsTyping(false);
    }
  };

  const finishConversation = () => {
    setIsFinishedConversation(true);
    setMessages((prevMessages) => [...prevMessages, createNewAssistantMessage('Bye! 👋')]);
    setHistoricMessages((prevMessages) => [...prevMessages, {
      id: prevMessages.length + 1,
      title: `Conversation ${user || 'user'} #${prevMessages.length + 1} - ${new Date().toLocaleString()}`,
      messages,
    }]);
    setUser('');
    setTimeout(() => {
      resetMessageIdCounter();
      setMessages([firstMessage]);
      setIsFinishedConversation(false);
    }, 2000);
  };

  const sendMessage = (message) => {
    setMessages((prev) => [...prev, createNewUserMessage(message)]);
    getBotResponse(message);
  };

  const contextType = useMemo(
    () => (
      {
        messages, sendMessage, historicMessages, isTyping, isFinishedConversation,
      }),
    [messages, sendMessage, historicMessages, isTyping, isFinishedConversation],
  );

  return (
    <ChatContext.Provider value={contextType}>
      {children}
    </ChatContext.Provider>
  );
}

ChatProvider.propTypes = {
  children: PropTypes.node.isRequired,
};
