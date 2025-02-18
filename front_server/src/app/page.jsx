import React from 'react';
import { Header } from '@/components';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import Chat from '@/components/chat/Chat';

export default function Home() {
  return (
    <main className="flex flex-col max-w-5xl m-auto min-h-screen">
      <Header />
      <ProtectedRoute>
        <Chat />
      </ProtectedRoute>
    </main>
  );
}
