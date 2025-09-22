'use client';

import { Button } from '@/components/ui/button';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export default function SettingsPage() {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const { mutate: logout } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        // Clear any client-side state and redirect to home
        router.push('/');
        router.refresh();
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        // Even if logout fails, redirect to home (cookies might be cleared server-side)
        router.push('/');
        router.refresh();
      },
      onSettled: () => {
        setIsSigningOut(false);
      },
    },
  });

  const handleSignOut = () => {
    setIsSigningOut(true);
    logout();
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg bg-gray-900 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">
          Account Settings
        </h2>
        <p className="mb-6 text-gray-400">
          Manage your account preferences and settings.
        </p>

        <Button
          variant="outline"
          size="sm"
          onClick={handleSignOut}
          disabled={isSigningOut}
        >
          {isSigningOut ? 'Signing out...' : 'Sign out'}
        </Button>
      </div>
    </div>
  );
}
