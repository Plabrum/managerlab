import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { CheckCircle } from 'lucide-react';

interface MagicLinkSuccessProps {
  email: string;
  onTryAgain: () => void;
}

export function MagicLinkSuccess({ email, onTryAgain }: MagicLinkSuccessProps) {
  return (
    <div className="flex h-screen items-center justify-center overflow-auto bg-black p-4">
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
            Click the link in your email to sign in. The link will expire in 15
            minutes.
          </p>
          <Button
            variant="ghost"
            className="w-full text-zinc-400 hover:text-white"
            onClick={onTryAgain}
          >
            Try a different email
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
