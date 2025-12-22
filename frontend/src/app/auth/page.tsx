'use client';

import type React from 'react';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Script from 'next/script';
import { useAuthMagicLinkRequestRequestMagicLink } from '@/openapi/auth/auth';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { handleError } from '@/lib/error-handler';
import {
  MagicLinkSuccess,
  GoogleSignInButton,
  MagicLinkForm,
  AuthFormLayout,
} from '@/components/auth';

// Extend window to include grecaptcha
declare global {
  interface Window {
    grecaptcha: {
      ready: (callback: () => void) => void;
      execute: (
        siteKey: string,
        options: { action: string }
      ) => Promise<string>;
    };
  }
}

const RECAPTCHA_SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || '';

function AuthContent() {
  const searchParams = useSearchParams();
  const isSignUp = searchParams.get('sign-up') !== null;

  const [email, setEmail] = useState('');
  const [honeypot, setHoneypot] = useState('');
  const [magicLinkSent, setMagicLinkSent] = useState(false);

  const magicLinkMutation = useAuthMagicLinkRequestRequestMagicLink({
    mutation: {
      onSuccess: () => setMagicLinkSent(true),
      onError: (error) => {
        handleError(error, {
          fallbackMessage: 'Failed to send magic link. Please try again.',
        });
      },
    },
  });

  const handleGoogleSignIn = () => {
    const baseUrl = (
      process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
    ).replace(/\/$/, '');

    // Build return URL using current origin (supports preview deployments)
    const returnUrl = `${window.location.origin}/dashboard`;

    window.location.href = `${baseUrl}/auth/google/login?return_url=${encodeURIComponent(returnUrl)}`;
  };

  const handleMagicLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    try {
      // Get reCAPTCHA token (skip if not configured)
      let recaptchaToken = '';
      const hasValidKey =
        RECAPTCHA_SITE_KEY && !RECAPTCHA_SITE_KEY.includes('your_recaptcha');

      if (hasValidKey && window.grecaptcha) {
        recaptchaToken = await window.grecaptcha.execute(RECAPTCHA_SITE_KEY, {
          action: 'magic_link_request',
        });
      }

      magicLinkMutation.mutate({
        data: {
          email,
          recaptcha_token: recaptchaToken,
          honeypot,
        },
      });
    } catch (error) {
      handleError(error, {
        fallbackMessage: 'Failed to verify request. Please try again.',
      });
    }
  };

  const handleTryAgain = () => {
    setMagicLinkSent(false);
    setEmail('');
  };

  if (magicLinkSent) {
    return <MagicLinkSuccess email={email} onTryAgain={handleTryAgain} />;
  }

  return (
    <AuthFormLayout
      isSignUp={isSignUp}
      googleButton={
        <GoogleSignInButton
          disabled={magicLinkMutation.isPending}
          onSignIn={handleGoogleSignIn}
        />
      }
      magicLinkForm={
        <MagicLinkForm
          email={email}
          honeypot={honeypot}
          isSubmitting={magicLinkMutation.isPending}
          onEmailChange={setEmail}
          onHoneypotChange={setHoneypot}
          onSubmit={handleMagicLinkSubmit}
        />
      }
    />
  );
}

export default function AuthPage() {
  // Only load reCAPTCHA script if valid key is configured
  const hasValidKey =
    RECAPTCHA_SITE_KEY && !RECAPTCHA_SITE_KEY.includes('your_recaptcha');

  return (
    <>
      {/* Load reCAPTCHA v3 script */}
      {hasValidKey && (
        <Script
          src={`https://www.google.com/recaptcha/api.js?render=${RECAPTCHA_SITE_KEY}`}
          strategy="lazyOnload"
        />
      )}
      <SuspenseWrapper>
        <AuthContent />
      </SuspenseWrapper>
    </>
  );
}
