'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/provider/AuthContext';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from '@components/ui/card';
import { Input } from '@components/ui/input';
import { Button } from '@components/ui/button';
import axios from 'axios';

export default function Login() {
  const router = useRouter();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    uid: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('http://localhost:30002/auth/login', formData);
      if (response.data.user) {
        login(response.data.user);
        router.push('/');
      }
    } catch (err) {
      setError(err.response?.data?.detail || '로그인에 실패했습니다.');
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>로그인</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Input
                placeholder="아이디"
                value={formData.uid}
                onChange={(e) => setFormData({...formData, uid: e.target.value})}
              />
              <Input
                type="password"
                placeholder="비밀번호"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <Button type="submit" className="w-full">로그인</Button>
          </form>
          <div className="mt-4 text-center">
            <Link href="/signup" className="text-sm text-blue-500 hover:underline">
              회원가입하기
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}