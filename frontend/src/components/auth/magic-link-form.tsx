import { Mail } from 'lucide-react';
import type React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface MagicLinkFormProps {
  email: string;
  honeypot: string;
  isSubmitting: boolean;
  onEmailChange: (email: string) => void;
  onHoneypotChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}

export function MagicLinkForm({
  email,
  honeypot,
  isSubmitting,
  onEmailChange,
  onHoneypotChange,
  onSubmit,
}: MagicLinkFormProps) {
  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="email" className="text-zinc-300">
          Email address
        </Label>
        <Input
          id="email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => onEmailChange(e.target.value)}
          required
          className="border-zinc-700 bg-zinc-800 text-white placeholder:text-zinc-500"
        />
      </div>

      {/* Honeypot field - hidden from real users, bots often fill it */}
      <input
        type="text"
        name="website"
        value={honeypot}
        onChange={(e) => onHoneypotChange(e.target.value)}
        style={{
          position: 'absolute',
          left: '-9999px',
          width: '1px',
          height: '1px',
          opacity: 0,
          pointerEvents: 'none',
        }}
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
      />

      <Button
        type="submit"
        disabled={isSubmitting || !email}
        className="w-full bg-zinc-800 text-white hover:bg-zinc-700"
        size="lg"
      >
        {isSubmitting ? (
          <>Sending...</>
        ) : (
          <>
            <Mail className="mr-2 h-4 w-4" />
            Send magic link
          </>
        )}
      </Button>
    </form>
  );
}
