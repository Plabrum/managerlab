import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC = new Set([
  '/',
  '/auth',
  '/terms',
  '/privacy',
  '/favicon.ico',
  '/robots.txt',
  '/sitemap.xml',
  '/manifest.webmanifest',
]);

function normalize(path: string) {
  // strip trailing slash except for root
  return path !== '/' ? path.replace(/\/+$/, '') : '/';
}

function isPublic(pathname: string) {
  const path = normalize(pathname);
  if (PUBLIC.has(path)) return true;
  return (
    path.startsWith('/_next') ||
    path.startsWith('/static') ||
    path.startsWith('/images') ||
    path.startsWith('/fonts')
  );
}

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const path = normalize(pathname);

  // Handle /auth/expire even with locales/basePath/trailing slash
  const isExpire = path.endsWith('/auth/expire');

  if (isExpire) {
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

  if (isPublic(pathname)) return NextResponse.next();

  const hasSession = Boolean(req.cookies.get('session')?.value);
  if (!hasSession) {
    return NextResponse.redirect(new URL('/auth', req.url));
  }

  return NextResponse.next();
}

export const config = {
  // Run on everything (you can exclude assets with isPublic)
  matcher: ['/:path*'],
};
