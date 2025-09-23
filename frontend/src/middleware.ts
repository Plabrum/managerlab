import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const res = NextResponse.redirect(new URL('/auth', req.url));
  // If you need this to work on localhost HTTP, drop `secure: true` in dev
  res.cookies.set({
    name: 'session',
    value: '',
    path: '/',
    expires: new Date(0),
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
  });
  return res;
}

export const config = {
  matcher: ['/auth/expire'],
};
