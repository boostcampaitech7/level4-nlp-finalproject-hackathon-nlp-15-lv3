'use client';

import React, {
  useContext, useState, useRef, useEffect,
} from 'react';
import {
  Card, CardHeader, CardTitle, CardContent, CardFooter, CardDescription,
} from '@components/ui/card';
import { Input } from '@components/ui/input';
import { Button } from '@components/ui/button';
import { ScrollArea } from '@components/ui/scroll-area';
import { ChatContext } from '@/provider';
import BotCardContent from './BotCardContent';
import BotMessageWithOptions from './BotMessageWithOptions';
import UserMessage from './UserMessage';
import BotMessageWithReference from './BotMessageWithReference';
import LoadingDots from './LoadingDots';
import ReactMarkdown from 'react-markdown';

export default function Chat() {
  const {
    messages, 
    sendMessage, 
    isTyping, 
    isFinishedConversation,
    useWebSearch,
    setUseWebSearch,
  } = useContext(ChatContext);
  const [chatInput, setChatInput] = useState('');
  const lastMessageRef = useRef(null);

  useEffect(() => {
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    sendMessage(chatInput);
    setChatInput('');
  };

  const renderBotMessage = (message) => {
    if (message.options) {
      return (
        <BotMessageWithOptions
          key={message.id}
          message={message.content}
          options={message.options}
        />
      );
    }
    if (message.reference) {
      return (
        <BotMessageWithReference
          key={message.id}
          message={message.content}
          reference={message.reference}
        />
      );
    }

    return (
      <BotCardContent key={message.id}>
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </BotCardContent>
    );
  };

  return (
    <section className="self-center">
      <Card className="w-[1200px]">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Chatbot</CardTitle>
              <CardDescription>채팅으로 질문해보세요</CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                웹 검색 {useWebSearch ? "켜짐" : "꺼짐"}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setUseWebSearch(!useWebSearch)}
              >
                {useWebSearch ? "웹 검색 끄기" : "웹 검색 켜기"}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[600px] w-full pr-4 mt-2">
            {
            messages.map((message, index) => (message.role === 'assistant'
              ? (
                <div
                  ref={index === messages.length - 1 ? lastMessageRef : null}
                  key={message.id}
                >
                  {renderBotMessage(message)}
                </div>
              )
              : <UserMessage key={message.id} message={message} />))
          }
            {isTyping && <LoadingDots />}
          </ScrollArea>
        </CardContent>
        <CardFooter>
          <form onSubmit={handleSubmit} className="w-full flex gap-2">
            <Input
              placeholder="How can I help you?"
              value={chatInput}
              disabled={isFinishedConversation}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <Button disabled={isFinishedConversation} type="submit">Send</Button>
          </form>
        </CardFooter>
      </Card>
    </section>
  );
}
