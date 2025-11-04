import { NextRequest, NextResponse } from 'next/server';
import { config as appConfig } from '@/lib/config';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Only run middleware for authenticated routes (not auth pages)
  if (pathname.startsWith('/auth') || pathname === '/') {
    return NextResponse.next();
  }

  // Skip middleware for onboarding page itself
  if (pathname.startsWith('/onboarding')) {
    return NextResponse.next();
  }

  // For authenticated routes, check if user has teams
  // We need to call the backend to check teams
  try {
    const teamsResponse = await fetch(`${appConfig.api.baseUrl}/users/teams`, {
      headers: {
        cookie: request.headers.get('cookie') || '',
      },
      credentials: 'include',
    });

    if (!teamsResponse.ok) {
      // If not authenticated, let the page handle it
      if (teamsResponse.status === 401) {
        return NextResponse.next();
      }
      // Other errors, let the page handle it
      return NextResponse.next();
    }

    const teamsData = await teamsResponse.json();

    // If user has no teams, redirect to onboarding
    if (teamsData.teams && teamsData.teams.length === 0) {
      return NextResponse.redirect(new URL('/onboarding', request.url));
    }

    // User has teams, continue to requested page
    return NextResponse.next();
  } catch (error) {
    // On error, let the page handle it (don't block the request)
    console.error('[Middleware] Error checking teams:', error);
    return NextResponse.next();
  }
}

// Configure which routes use this middleware
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
