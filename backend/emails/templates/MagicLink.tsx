import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';
import { colors, spacing, typography, borderRadius } from '../design-tokens';

interface MagicLinkProps {
  magic_link_url: string;
  expiration_minutes: string | number;
}

export default function MagicLink({
  magic_link_url,
  expiration_minutes,
}: MagicLinkProps) {
  return (
    <BaseLayout preview="Sign in to your account securely">
      <Section style={styles.headingSection}>
        <Heading style={styles.heading}>Sign in to your account</Heading>
      </Section>

      <Text style={styles.paragraph}>
        Click the button below to securely sign in. This link expires in{' '}
        {expiration_minutes} minutes for your security.
      </Text>

      <Section style={styles.buttonContainer}>
        <Button href={magic_link_url}>Continue to Arive</Button>
      </Section>

      {/* Alternative link section */}
      <Section style={styles.alternativeSection}>
        <Text style={styles.alternativeLabel}>Or copy this link:</Text>
        <div style={styles.urlBox}>
          <Text style={styles.urlText}>{magic_link_url}</Text>
        </div>
      </Section>

      {/* Security notice */}
      <Section style={styles.securityNotice}>
        <Text style={styles.securityText}>
          <strong style={styles.securityHeading}>Didn't request this?</strong>
          <br />
          You can safely ignore this email. This link can only be used once and
          expires automatically.
        </Text>
      </Section>
    </BaseLayout>
  );
}

const styles = {
  headingSection: {
    marginBottom: spacing.lg,
  },
  heading: {
    color: colors.foreground,
    fontSize: '28px',
    fontWeight: typography.weightBold,
    margin: 0,
    lineHeight: typography.lineHeightTight,
    letterSpacing: '-0.02em',
  },
  paragraph: {
    color: colors.foregroundMuted,
    fontSize: '16px',
    lineHeight: typography.lineHeightRelaxed,
    margin: `0 0 ${spacing.xl} 0`,
    fontWeight: typography.weightNormal,
  },
  buttonContainer: {
    margin: `${spacing.xl} 0`,
    textAlign: 'center' as const,
  },
  alternativeSection: {
    marginTop: spacing['2xl'],
    marginBottom: spacing.xl,
  },
  alternativeLabel: {
    fontSize: '13px',
    color: colors.foregroundSubtle,
    margin: `0 0 ${spacing.sm} 0`,
    fontWeight: typography.weightMedium,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  urlBox: {
    backgroundColor: colors.backgroundMuted,
    border: `1px solid ${colors.border}`,
    borderRadius: borderRadius.md,
    padding: `${spacing.md} ${spacing.md}`,
  },
  urlText: {
    color: colors.foregroundMuted,
    fontSize: '13px',
    wordBreak: 'break-all' as const,
    margin: 0,
    lineHeight: typography.lineHeightNormal,
    fontFamily: typography.fontFamilyMono,
  },
  securityNotice: {
    marginTop: spacing['2xl'],
    padding: spacing.md,
    backgroundColor: colors.backgroundMuted,
    borderRadius: borderRadius.md,
    border: `1px solid ${colors.borderSubtle}`,
  },
  securityHeading: {
    color: colors.foreground,
    fontWeight: typography.weightSemibold,
  },
  securityText: {
    color: colors.foregroundMuted,
    fontSize: '14px',
    lineHeight: typography.lineHeightRelaxed,
    margin: 0,
  },
};
