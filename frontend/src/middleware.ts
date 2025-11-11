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

  // For authenticated routes, check user state and redirect to onboarding if needed
  try {
    // Fetch current user to check their state
    const userResponse = await fetch(
      `${appConfig.api.baseUrl}/users/current_user`,
      {
        headers: {
          cookie: request.headers.get('cookie') || '',
        },
        credentials: 'include',
      }
    );

    if (!userResponse.ok) {
      // If not authenticated, let the page handle it
      if (userResponse.status === 401) {
        return NextResponse.next();
      }
      // Other errors, let the page handle it
      return NextResponse.next();
    }

    const userData = await userResponse.json();

    // If user is in NEEDS_TEAM state, redirect to onboarding
    if (userData.state === 'needs_team') {
      return NextResponse.redirect(new URL('/onboarding', request.url));
    }

    // User is in valid state, continue to requested page
    return NextResponse.next();
  } catch (error) {
    // On error, let the page handle it (don't block the request)
    console.error('[Middleware] Error checking user state:', error);
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
