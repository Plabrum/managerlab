import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  // Handle auth expiration
  if (req.nextUrl.pathname === '/auth/expire') {
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

  // Add pathname to headers for server components
  const requestHeaders = new Headers(req.headers);
  requestHeaders.set('x-pathname', req.nextUrl.pathname);

  return NextResponse.next({
    request: {
      headers: requestHeaders,
    },
  });
}

export const config = {
  matcher: [
    '/auth/expire',
    '/dashboard/:path*',
    '/onboarding/:path*',
    '/campaigns/:path*',
    '/brands/:path*',
    '/roster/:path*',
    '/posts/:path*',
    '/media/:path*',
    '/invoices/:path*',
    '/users/:path*',
    '/settings/:path*',
    '/brandcontacts/:path*',
  ],
};
