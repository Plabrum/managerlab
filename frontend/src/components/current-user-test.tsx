'use client';

import { useUsersCurrentUserGetCurrentUser } from '@/openapi/users/users';
import { Suspense } from 'react';

function CurrentUserContent() {
  const { data: user, error, isLoading } = useUsersCurrentUserGetCurrentUser();

  if (isLoading) {
    return (
      <div className="rounded-lg border p-4">
        <div className="animate-pulse">
          <div className="mb-2 h-4 w-3/4 rounded bg-gray-200"></div>
          <div className="h-4 w-1/2 rounded bg-gray-200"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <h3 className="text-sm font-medium text-red-800">
          Authentication Test Failed
        </h3>
        <p className="mt-1 text-sm text-red-600">
          Error loading user data - please try logging in
        </p>
      </div>
    );
  }

  if (user) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4">
        <h3 className="text-sm font-medium text-green-800">
          ✅ Authentication Working!
        </h3>
        <div className="mt-2 text-sm text-green-700">
          <p>
            <strong>ID:</strong> {user.id}
          </p>
          <p>
            <strong>Name:</strong> {user.name}
          </p>
          <p>
            <strong>Email:</strong> {user.email}
          </p>
          <p>
            <strong>Verified:</strong> {user.email_verified ? 'Yes' : 'No'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm text-gray-600">No user data received</p>
    </div>
  );
}

export function CurrentUserTest() {
  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold">Auth Test: Current User</h3>
      <Suspense
        fallback={
          <div className="rounded-lg border p-4">
            <div className="text-sm text-gray-600">Loading user data...</div>
          </div>
        }
      >
        <CurrentUserContent />
      </Suspense>
    </div>
  );
}
