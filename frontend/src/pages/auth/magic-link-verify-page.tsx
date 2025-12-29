import { useEffect } from 'react';
import { useNavigate, useSearch } from '@tanstack/react-router';

export function MagicLinkVerifyPage() {
  const navigate = useNavigate();
  const search = useSearch({ from: '/_public/auth/magic-link/verify' });

  useEffect(() => {
    const verifyToken = async () => {
      const token = search.token;

      if (!token) {
        // No token provided, redirect to auth page
        navigate({ to: '/auth' });
        return;
      }

      try {
        // The backend endpoint handles verification and creates the session
        const response = await fetch(
          `/api/magic-link/verify?token=${encodeURIComponent(token)}`,
          {
            method: 'GET',
            credentials: 'include', // Important for session cookies
          }
        );

        if (response.ok) {
          // Backend sets the session and redirects
          // Follow the redirect or navigate to dashboard
          window.location.href = '/dashboard';
        } else {
          // Verification failed, redirect to auth with error
          navigate({ to: '/auth', search: { error: 'invalid_link' } });
        }
      } catch {
        // Network error or other issue
        navigate({ to: '/auth', search: { error: 'verification_failed' } });
      }
    };

    verifyToken();
  }, [search.token, navigate]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-black">
      <div className="text-center">
        <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent" />
        <p className="text-white">Verifying magic link...</p>
      </div>
    </div>
  );
}
