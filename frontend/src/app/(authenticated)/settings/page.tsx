'use client';

import { Button } from '@/components/ui/button';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { ThemeSwitcherInline } from '@/components/theme-switcher';

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
      <div className="bg-card rounded-lg border p-6">
        <h2 className="mb-4 text-xl font-semibold">Account Settings</h2>
        <p className="text-muted-foreground mb-6">
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

      <div className="bg-card rounded-lg border p-6">
        <h2 className="mb-4 text-xl font-semibold">Appearance</h2>
        <p className="text-muted-foreground mb-6">
          Choose how Arive looks to you. Select a single theme, or sync with
          your system.
        </p>

        <ThemeSwitcherInline />
      </div>
    </div>
  );
}
