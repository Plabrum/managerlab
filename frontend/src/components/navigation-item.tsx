'use client';

import type React from 'react';

interface NavigationItemProps {
  href: string;
  children: React.ReactNode;
}

export function NavigationItem({ href, children }: NavigationItemProps) {
  return (
    <a
      href={href}
      className="scroll-smooth rounded-md px-3 py-2 text-sm font-medium text-gray-300 transition-colors hover:text-white"
      onClick={(e) => {
        e.preventDefault();
        document
          .getElementById(href.slice(1))
          ?.scrollIntoView({ behavior: 'smooth' });
      }}
    >
      {children}
    </a>
  );
}
