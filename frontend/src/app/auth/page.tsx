'use client';

import type React from 'react';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import Link from 'next/link';

export default function AuthPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [magicLinkSent, setMagicLinkSent] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      const baseUrl = (
        process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
      ).replace(/\/$/, '');
      window.location.href = `${baseUrl}/auth/google/login`;
    } catch (error) {
      console.error('Google sign in error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMagicLinkSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setIsLoading(true);
    try {
      // TODO: Implement magic link sending
      console.log('Magic link requested for:', email);
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setMagicLinkSent(true);
    } catch (error) {
      console.error('Magic link error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (magicLinkSent) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-black p-4">
        <Card className="w-full max-w-md border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-600">
              <CheckCircle className="h-6 w-6 text-white" />
            </div>
            <CardTitle className="text-white">Check your email</CardTitle>
            <CardDescription className="text-zinc-400">
              We&apos;ve sent a magic link to{' '}
              <strong className="text-white">{email}</strong>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-sm text-zinc-400">
              Click the link in your email to sign in. The link will expire in
              15 minutes.
            </p>
            <Button
              variant="ghost"
              className="w-full text-zinc-400 hover:text-white"
              onClick={() => {
                setMagicLinkSent(false);
                setEmail('');
              }}
            >
              Try a different email
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-black p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Back to home link */}
        <Link
          href="/"
          className="inline-flex items-center text-zinc-400 transition-colors hover:text-white"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Arive
        </Link>

        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">Welcome back</CardTitle>
            <CardDescription className="text-zinc-400">
              Sign in to your Arive account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Google Sign In */}
            <Button
              onClick={handleGoogleSignIn}
              disabled={isLoading}
              className="w-full bg-white font-medium text-black hover:bg-gray-100"
              size="lg"
            >
              <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Continue with Google
            </Button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full bg-zinc-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-zinc-900 px-2 text-zinc-400">Or</span>
              </div>
            </div>

            {/* Magic Link Form */}
            <form onSubmit={handleMagicLinkSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-zinc-300">
                  Email address
                </Label>
                {/* <Input */}
                {/*   id="email" */}
                {/*   type="email" */}
                {/*   placeholder="Enter your email" */}
                {/*   value={email} */}
                {/*   onChange={(e) => setEmail(e.target.value)} */}
                {/*   required */}
                {/*   className="border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500" */}
                {/* /> */}
                <div className="group relative w-full">
                  <Input
                    id="email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500"
                    disabled
                  />
                  <div
                    role="tooltip"
                    className="pointer-events-none absolute left-0 top-full z-10 mt-1 hidden rounded bg-zinc-900 px-2 py-1 text-xs text-white shadow group-hover:block"
                  >
                    Magic link sign-in is coming soon.
                  </div>
                </div>
              </div>
              <Button
                type="submit"
                disabled={isLoading || !email}
                className="w-full bg-zinc-800 text-white hover:bg-zinc-700"
                size="lg"
              >
                <Mail className="mr-2 h-4 w-4" />
                Send magic link
              </Button>
            </form>

            <p className="text-center text-xs text-zinc-500">
              By signing in, you agree to our{' '}
              <Link
                href="/terms"
                className="text-zinc-400 underline hover:text-white"
              >
                Terms of Service
              </Link>{' '}
              and{' '}
              <Link
                href="/privacy"
                className="text-zinc-400 underline hover:text-white"
              >
                Privacy Policy
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
