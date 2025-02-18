'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
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

export default function SignUp() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    uid: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }

    try {
      await axios.post('http://localhost:30002/auth/signup', {
        uid: formData.uid,
        password: formData.password,
      });
      
      router.push('/login');
    } catch (err) {
      setError(err.response?.data?.detail || '회원가입 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <Card className="w-[400px]">
        <CardHeader>
          <CardTitle>회원가입</CardTitle>
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
              <Input
                type="password"
                placeholder="비밀번호 확인"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <Button type="submit" className="w-full">회원가입</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}