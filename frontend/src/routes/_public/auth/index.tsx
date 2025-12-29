import { createFileRoute } from '@tanstack/react-router';
import type React from 'react';
import { useState } from 'react';
import { useSearch } from '@tanstack/react-router';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { handleError } from '@/lib/error-handler';
import { useAuthMagicLinkRequestRequestMagicLink } from '@/openapi/auth/auth';

export const Route = createFileRoute('/_public/auth/')({
  component: AuthPage,
});

function AuthPage() {
  // Only load reCAPTCHA script if valid key is configured
  const hasValidKey =
    RECAPTCHA_SITE_KEY && !RECAPTCHA_SITE_KEY.includes('your_recaptcha');

  return (
    <>
      {/* Load reCAPTCHA v3 script */}
      {hasValidKey && (
        <script
          src={`https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`}
          async
          defer
        />
      )}
      <SuspenseWrapper>
        <AuthContent />
      </SuspenseWrapper>
    </>
  );
}
