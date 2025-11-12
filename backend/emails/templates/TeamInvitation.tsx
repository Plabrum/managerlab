import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';
import { colors, spacing } from '../design-tokens';

interface TeamInvitationProps {
  invitation_url: string;
  team_name: string;
  inviter_name: string;
  expiration_hours: string | number;
}

export default function TeamInvitation({
  invitation_url,
  team_name,
  inviter_name,
  expiration_hours,
}: TeamInvitationProps) {
  return (
    <BaseLayout preview={`You're invited to join ${team_name} on Arive`}>
      <Heading style={styles.heading}>
        You're Invited to Join {team_name} on Arive
      </Heading>

      <Text style={styles.paragraph}>Hello,</Text>

      <Text style={styles.paragraph}>
        <strong>{inviter_name}</strong> has invited you to join the{' '}
        <strong>{team_name}</strong> team on Arive.
      </Text>

      <Section style={styles.infoBox}>
        <Text style={styles.infoText}>
          <strong>Team:</strong> {team_name}
          <br />
          <strong>Invited by:</strong> {inviter_name}
        </Text>
      </Section>

      <Section style={styles.buttonContainer}>
        <Button href={invitation_url}>Accept Invitation</Button>
      </Section>

      <Text style={styles.paragraph}>
        Or copy and paste this URL into your browser:
      </Text>

      <Text style={styles.urlText}>{invitation_url}</Text>

      <Section style={styles.notice}>
        <Text style={styles.noticeText}>
          <strong>This invitation expires in {expiration_hours} hours.</strong>
          <br />
          If you don't accept it within that time, you'll need to request a new
          invitation.
        </Text>
      </Section>

      <Section style={styles.securityNotice}>
        <Text style={styles.securityText}>
          <strong>Didn't expect this invitation?</strong>
          <br />
          If you didn't request to join this team, you can safely ignore this
          email. No action will be taken on your account.
        </Text>
      </Section>
    </BaseLayout>
  );
}

const styles = {
  heading: {
    color: colors.foreground,
    fontSize: '24px',
    fontWeight: 600,
    margin: '0 0 24px 0',
    lineHeight: '1.3',
  },
  paragraph: {
    color: colors.foreground,
    fontSize: '16px',
    lineHeight: '1.6',
    margin: '0 0 16px 0',
  },
  infoBox: {
    margin: `${spacing.lg} 0`,
    padding: spacing.lg,
    backgroundColor: colors.muted,
    borderLeft: `4px solid ${colors.primary}`,
    borderRadius: '6px',
  },
  infoText: {
    color: colors.foreground,
    fontSize: '15px',
    lineHeight: '1.8',
    margin: 0,
  },
  buttonContainer: {
    textAlign: 'center' as const,
    margin: `${spacing.lg} 0`,
  },
  urlText: {
    color: colors.mutedForeground,
    fontSize: '14px',
    wordBreak: 'break-all' as const,
    margin: '0 0 24px 0',
    lineHeight: '1.5',
  },
  notice: {
    marginTop: spacing.lg,
  },
  noticeText: {
    color: colors.mutedForeground,
    fontSize: '14px',
    lineHeight: '1.6',
    margin: 0,
  },
  securityNotice: {
    marginTop: spacing.lg,
  },
  securityText: {
    color: colors.mutedForeground,
    fontSize: '14px',
    lineHeight: '1.6',
    margin: 0,
  },
};
