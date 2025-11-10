'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function InviteAcceptPage() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');

    if (!token) {
      // No token provided, redirect to auth page
      window.location.href = '/auth?error=missing_token';
      return;
    }

    // Redirect to backend accept endpoint
    // Backend will verify token, create/link user, create session, and redirect back to app
    const baseUrl = (
      process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
    ).replace(/\/$/, '');

    window.location.href = `${baseUrl}/teams/invitations/accept?token=${encodeURIComponent(token)}`;
  }, [searchParams]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <div className="text-center">
        <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent" />
        <p className="text-white">Accepting your invitation...</p>
      </div>
    </div>
  );
}
