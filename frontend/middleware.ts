import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const AUTH_COOKIE_NAME = 'session';
const SIGNIN_PATH = '/auth';
const PROTECTED_MATCHERS = ['/home'];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  const isProtectedRoute = PROTECTED_MATCHERS.some((path) =>
    pathname.startsWith(path)
  );

  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  const hasSession = Boolean(req.cookies.get(AUTH_COOKIE_NAME));
  if (hasSession) {
    return NextResponse.next();
  }

  const redirectUrl = req.nextUrl.clone();
  redirectUrl.pathname = SIGNIN_PATH;
  redirectUrl.search = '';

  return NextResponse.redirect(redirectUrl);
}

export const config = {
  matcher: ['/home/:path*'],
};
