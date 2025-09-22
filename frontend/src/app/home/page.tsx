'use client';

import { useAuth } from '@/components/provers/auth-provider';

export default function HomePage() {
  const user = useAuth();
  return (
    <div className="space-y-8">
      <section className="rounded-lg border border-green-200 bg-green-50 p-6">
        <h1 className="text-xl font-semibold text-green-800">
          Welcome back, {user.name || user.email}!
        </h1>
        <p className="mt-2 text-sm text-green-700">
          You are signed in and ready to use ManageOS.
        </p>
        <div className="mt-4 grid gap-2 text-sm text-green-800 sm:grid-cols-2">
          <p>
            <span className="font-medium">User ID:</span> {user.id}
          </p>
          <p>
            <span className="font-medium">Email:</span> {user.email}
          </p>
          <p>
            <span className="font-medium">Verified:</span>{' '}
            {user.email_verified ? 'Yes' : 'No'}
          </p>
        </div>
      </section>
    </div>
  );
}
