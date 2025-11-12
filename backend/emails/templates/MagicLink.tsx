import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';
import { colors, spacing } from '../design-tokens';

interface MagicLinkProps {
  magic_link_url: string;
  expiration_minutes: string | number;
}

export default function MagicLink({
  magic_link_url,
  expiration_minutes,
}: MagicLinkProps) {
  return (
    <BaseLayout preview="Sign in to your Arive account">
      <Heading style={styles.heading}>Sign in to Arive</Heading>

      <Text style={styles.paragraph}>Hello,</Text>

      <Text style={styles.paragraph}>
        Click the button below to sign in to your Arive account. This link will
        expire in {expiration_minutes} minutes.
      </Text>

      <Section style={styles.buttonContainer}>
        <Button href={magic_link_url}>Sign In to Arive</Button>
      </Section>

      <Text style={styles.paragraph}>
        Or copy and paste this URL into your browser:
      </Text>

      <Text style={styles.urlText}>{magic_link_url}</Text>

      <Section style={styles.securityNotice}>
        <Text style={styles.securityText}>
          <strong>Didn't request this email?</strong>
          <br />
          If you didn't request this sign-in link, you can safely ignore this
          email. Someone may have entered your email address by mistake.
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
  securityNotice: {
    marginTop: spacing.xl,
  },
  securityText: {
    color: colors.mutedForeground,
    fontSize: '14px',
    lineHeight: '1.6',
    margin: 0,
  },
};
