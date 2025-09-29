'use client';

import { GetUserUserResponseBody } from '@/openapi/managerLab.schemas';
import { createContext, useContext } from 'react';

// Create context that *can* be null internally
const AuthCtx = createContext<GetUserUserResponseBody | null>(null);

export function useAuth(): GetUserUserResponseBody {
  const ctx = useContext(AuthCtx);
  if (!ctx) {
    throw new Error(
      'useAuth must be used within an <AuthProvider>. ' +
        'Did you forget to wrap your layout?'
    );
  }
  return ctx;
}

export function AuthProvider({
  user,
  children,
}: {
  user: GetUserUserResponseBody;
  children: React.ReactNode;
}) {
  return <AuthCtx.Provider value={user}>{children}</AuthCtx.Provider>;
}
