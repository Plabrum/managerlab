import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';

interface MagicLinkProps {
  magic_link_url: string;
  expiration_minutes: string | number;
}

export default function MagicLink({
  magic_link_url = 'https://app.tryarive.com/auth/magic-link?token=example',
  expiration_minutes = 15,
}: MagicLinkProps) {
  return (
    <BaseLayout preview="Sign in to your account securely">
      <Section className="mb-6">
        <Heading className="text-foreground text-[28px] font-bold m-0 leading-tight tracking-tight">
          Sign in to your account
        </Heading>
      </Section>

      <Text className="text-muted-foreground text-base leading-relaxed mb-8 font-normal">
        Click the button below to securely sign in. This link expires in{' '}
        {expiration_minutes} minutes for your security.
      </Text>

      <Section className="my-8 text-center">
        <Button href={magic_link_url}>Continue to Arive</Button>
      </Section>

      {/* Alternative link section */}
      <Section className="mt-12 mb-8">
        <Text className="text-[13px] text-neutral-400 mb-2 font-medium uppercase tracking-wider m-0">
          Or copy this link:
        </Text>
        <div className="bg-neutral-50 border border-border rounded-lg p-4">
          <Text className="text-muted-foreground text-[13px] break-all m-0 leading-normal font-mono">
            {magic_link_url}
          </Text>
        </div>
      </Section>

      {/* Security notice */}
      <Section className="mt-12 p-4 bg-neutral-50 rounded-lg border border-neutral-100">
        <Text className="text-muted-foreground text-sm leading-relaxed m-0">
          <strong className="text-foreground font-semibold">Didn't request this?</strong>
          <br />
          You can safely ignore this email. This link can only be used once and
          expires automatically.
        </Text>
      </Section>
    </BaseLayout>
  );
}
