import type { ReactNode } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface AuthFormLayoutProps {
  isSignUp: boolean;
  googleButton: ReactNode;
  magicLinkForm: ReactNode;
}

export function AuthFormLayout({
  isSignUp,
  googleButton,
  magicLinkForm,
}: AuthFormLayoutProps) {
  return (
    <div className="flex h-screen items-center justify-center overflow-auto bg-black p-4">
      <div className="w-full max-w-md space-y-6">
        <Link
          href="/"
          className="inline-flex items-center text-zinc-400 transition-colors hover:text-white"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Arive
        </Link>

        <Card className="border-zinc-800 bg-zinc-900">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl text-white">
              {isSignUp ? 'Create your account' : 'Welcome back'}
            </CardTitle>
            <CardDescription className="text-zinc-400">
              {isSignUp
                ? 'Sign up to get started with Arive'
                : 'Sign in to your Arive account'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {googleButton}

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator className="w-full bg-zinc-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-zinc-900 px-2 text-zinc-400">Or</span>
              </div>
            </div>

            {magicLinkForm}

            <p className="text-center text-xs text-zinc-500">
              By continuing, you agree to our{' '}
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

            {!isSignUp ? (
              <p className="text-center text-sm text-zinc-400">
                Don&apos;t have an account?{' '}
                <Link
                  href="/auth?sign-up"
                  className="text-white underline hover:text-zinc-300"
                >
                  Sign up
                </Link>
              </p>
            ) : (
              <p className="text-center text-sm text-zinc-400">
                Already have an account?{' '}
                <Link
                  href="/auth"
                  className="text-white underline hover:text-zinc-300"
                >
                  Sign in
                </Link>
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
