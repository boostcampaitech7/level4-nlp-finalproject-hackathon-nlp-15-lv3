import React from 'react';
import PropTypes from 'prop-types';
import './globals.css';
import { Inter } from 'next/font/google';
import { ChatProvider } from '../provider';
import { AuthProvider } from '@/provider/AuthContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'ChatBot',
  description: 'Web chatbot',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} bg-slate-50`}>
        <AuthProvider>
          <ChatProvider>
            {children}
          </ChatProvider>
        </AuthProvider>
      </body>
    </html>
  );
}

RootLayout.propTypes = {
  children: PropTypes.node.isRequired,
};
