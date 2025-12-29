import { createFileRoute } from '@tanstack/react-router';
import { Suspense, useEffect } from 'react';
import { useSearch } from '@tanstack/react-router';

export const Route = createFileRoute('/_public/invite.accept')({
  component: InviteAcceptPage,
});

function InviteAcceptPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-black">
          <div className="text-center">
            <div className="mb-4 inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-white border-r-transparent" />
            <p className="text-white">Loading...</p>
          </div>
        </div>
      }
    >
      <InviteAcceptContent />
    </Suspense>
  );
}
