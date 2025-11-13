import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';

interface TeamInvitationProps {
  invitation_url: string;
  team_name: string;
  inviter_name: string;
  expiration_hours: string | number;
}

export default function TeamInvitation({
  invitation_url = 'https://app.tryarive.com/teams/invitations/accept?token=example',
  team_name = 'Acme Corporation',
  inviter_name = 'John Doe',
  expiration_hours = 72,
}: TeamInvitationProps) {
  return (
    <BaseLayout preview={`You've been invited to join ${team_name}`}>
      <Section className="mb-6">
        <Heading className="text-foreground text-[28px] font-bold m-0 leading-tight tracking-tight">
          You've been invited!
        </Heading>
      </Section>

      <Text className="text-muted-foreground text-base leading-relaxed mb-8 font-normal">
        <strong className="text-foreground font-semibold">{inviter_name}</strong> has invited
        you to join <strong className="text-foreground font-semibold">{team_name}</strong> on
        Arive.
      </Text>

      {/* Team info card */}
      <Section className="bg-neutral-50 border border-border rounded-lg p-6 mb-8">
        <div className="flex justify-between items-center py-2">
          <Text className="text-[13px] text-neutral-400 m-0 font-medium uppercase tracking-wider">
            Team
          </Text>
          <Text className="text-[15px] text-foreground m-0 font-medium">{team_name}</Text>
        </div>
        <div className="h-px bg-border my-2" />
        <div className="flex justify-between items-center py-2">
          <Text className="text-[13px] text-neutral-400 m-0 font-medium uppercase tracking-wider">
            Invited by
          </Text>
          <Text className="text-[15px] text-foreground m-0 font-medium">{inviter_name}</Text>
        </div>
      </Section>

      <Section className="my-8 text-center">
        <Button href={invitation_url}>Accept invitation</Button>
      </Section>

      {/* Alternative link section */}
      <Section className="mt-12 mb-8">
        <Text className="text-[13px] text-neutral-400 mb-2 font-medium uppercase tracking-wider m-0">
          Or copy this link:
        </Text>
        <div className="bg-neutral-50 border border-border rounded-lg p-4">
          <Text className="text-muted-foreground text-[13px] break-all m-0 leading-normal font-mono">
            {invitation_url}
          </Text>
        </div>
      </Section>

      {/* Expiration notice */}
      <Section className="mt-8 mb-6 p-4 bg-green-50 rounded-lg border border-success">
        <Text className="text-foreground text-sm leading-relaxed m-0">
          <strong className="text-success font-semibold">
            This invitation expires in {expiration_hours} hours.
          </strong>
          <br />
          After that, you'll need to request a new one.
        </Text>
      </Section>

      {/* Security notice */}
      <Section className="mt-6 p-4 bg-neutral-50 rounded-lg border border-neutral-100">
        <Text className="text-muted-foreground text-sm leading-relaxed m-0">
          <strong className="text-foreground font-semibold">Not expecting this?</strong>
          <br />
          You can safely ignore this email. No action will be taken unless you
          accept the invitation.
        </Text>
      </Section>
    </BaseLayout>
  );
}
