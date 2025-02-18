'use client';

import React, { useState, useMemo, useEffect } from 'react';
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
  const [conversationId, setConversationId] = useState(''); // 대화 세션 ID 추가
  const [useWebSearch, setUseWebSearch] = useState(false);

  // 새로운 대화 세션 시작시 conversation_id 생성
  useEffect(() => {
    if (!conversationId) {
      setConversationId(Date.now().toString());
    }
  }, []);

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

  const parseReferences = (contextStr) => {
    if (!contextStr) return [];
    
    // 정규식을 사용하여 링크 패턴 매칭
    const pattern = /\[([^\]]+)\]\(([^)]+)\)/g;
    const references = [];
    let match;
  
    while ((match = pattern.exec(contextStr)) !== null) {
      references.push({
        title: match[1],
        url: match[2]
      });
    }
  
    return references;
  };

  const getBotResponse = async (message) => {
    setIsTyping(true);

    
    const payload = {
      uid: user || 'anonymous',
      conversation_id: conversationId,
      message: 
        { role: 'user', content: message }
      ,
      stream: false,
      top_k: 3,
      option: { 
        web: useWebSearch  // 웹 검색 옵션
      }
    };
    try {
      // axios 설정 추가
      const response = await axios.post('http://localhost:30002/chat', payload, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // 응답 처리
      if (response.data) {
        const references = parseReferences(response.data.context);
        const newMessage = createNewAssistantMessage(
          response.data.answer,
          null,
          references  // 파싱된 참조 배열 전달
        );
        setMessages(prev => [...prev, newMessage]);
        
        if (response.data.conversation_id) {
          setConversationId(response.data.conversation_id);
        }
      } else {
        handleFallbackAssistantResponse();
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
      conversationId,  // 대화 기록에 conversation_id 저장
    }]);
    setUser('');
    setTimeout(() => {
      resetMessageIdCounter();
      setMessages([firstMessage]);
      setIsFinishedConversation(false);
      setConversationId(Date.now().toString());  // 새로운 대화 세션 ID 생성
    }, 2000);
  };

  const sendMessage = (message) => {
    setMessages((prev) => [...prev, createNewUserMessage(message)]);
    getBotResponse(message);
  };

  const contextType = useMemo(
    () => (
      {
        messages, sendMessage, historicMessages, isTyping, isFinishedConversation, useWebSearch, setUseWebSearch,
      }),
    [messages, sendMessage, historicMessages, isTyping, isFinishedConversation, useWebSearch, setUseWebSearch],
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
