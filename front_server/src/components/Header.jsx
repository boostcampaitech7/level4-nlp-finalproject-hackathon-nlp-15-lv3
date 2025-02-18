'use client';

import React from 'react';
import Link from 'next/link';
import { useAuth } from '@/provider/AuthContext';
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
  navigationMenuTriggerStyle,
} from './ui/navigation-menu';

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <div className="flex justify-center w-full">
      <header className="w-[1200px] flex mt-5 mb-14 justify-between items-center px-5">
        {/* 좌측에 UID 표시 - 스타일 개선 */}
        <div className="px-4 py-2 bg-white rounded-lg shadow-sm border border-slate-200">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-sm font-medium text-slate-700">
              {user ? `${user.uid}님 환영합니다` : ''}
            </span>
          </div>
        </div>

        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem className="space-x-3">
              <Link href="/" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Chat
                </NavigationMenuLink>
              </Link>
              <Link href="/historic" legacyBehavior passHref>
                <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                  Historic
                </NavigationMenuLink>
              </Link>
              {user ? (
                <button
                  onClick={logout}
                  className={navigationMenuTriggerStyle()}
                >
                  로그아웃
                </button>
              ) : (
                <Link href="/login" legacyBehavior passHref>
                  <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                    로그인
                  </NavigationMenuLink>
                </Link>
              )}
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </header>
    </div>
  );
}
