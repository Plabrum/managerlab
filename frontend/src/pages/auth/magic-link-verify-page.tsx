import { Suspense, useEffect } from 'react';

export function MagicLinkVerifyPage() {
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
      <MagicLinkVerifyContent />
    </Suspense>
  );
}
