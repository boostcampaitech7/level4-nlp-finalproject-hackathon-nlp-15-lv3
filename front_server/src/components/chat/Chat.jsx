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
import { Globe } from 'lucide-react';

export default function Chat() {
  const {
    messages, 
    sendMessage, 
    isTyping, 
    isFinishedConversation,
    useWebSearch,
    setUseWebSearch,
    conversationId,  // ChatContext에서 conversationId 추가
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
              <div className="flex items-center gap-2">
                <CardTitle>Chatbot</CardTitle>
                {conversationId && (
                  <span className="text-xs px-2 py-1 bg-muted rounded-full text-muted-foreground">
                    ID: {conversationId.slice(-6)}
                  </span>
                )}
              </div>
              <CardDescription>
                채팅으로 질문해보세요
              </CardDescription>
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
          <form onSubmit={handleSubmit} className="w-full flex gap-2 items-center">
            <Input
              placeholder="How can I help you?"
              value={chatInput}
              disabled={isFinishedConversation}
              onChange={(e) => setChatInput(e.target.value)}
            />
            <Button
              type="button"
              variant={useWebSearch ? "default" : "outline"}
              size="icon"
              disabled={isFinishedConversation}
              onClick={() => setUseWebSearch(!useWebSearch)}
              className="w-10 h-10 p-2"
            >
              <Globe className="h-7 w-7" />
            </Button>
            <Button disabled={isFinishedConversation} type="submit">Send</Button>
          </form>
        </CardFooter>
      </Card>
    </section>
  );
}
