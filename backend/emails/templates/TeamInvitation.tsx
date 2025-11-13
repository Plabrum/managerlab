import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout } from './_BaseLayout';
import { Button } from './_Button';
import { colors, spacing, typography, borderRadius } from '../design-tokens';

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
    <BaseLayout preview={`You've been invited to join ${team_name}`}>
      <Section style={styles.headingSection}>
        <Heading style={styles.heading}>You've been invited!</Heading>
      </Section>

      <Text style={styles.paragraph}>
        <strong style={styles.inviterName}>{inviter_name}</strong> has invited
        you to join <strong style={styles.teamName}>{team_name}</strong> on
        Arive.
      </Text>

      {/* Team info card */}
      <Section style={styles.infoCard}>
        <div style={styles.infoRow}>
          <Text style={styles.infoLabel}>Team</Text>
          <Text style={styles.infoValue}>{team_name}</Text>
        </div>
        <div style={styles.dividerLine} />
        <div style={styles.infoRow}>
          <Text style={styles.infoLabel}>Invited by</Text>
          <Text style={styles.infoValue}>{inviter_name}</Text>
        </div>
      </Section>

      <Section style={styles.buttonContainer}>
        <Button href={invitation_url}>Accept invitation</Button>
      </Section>

      {/* Alternative link section */}
      <Section style={styles.alternativeSection}>
        <Text style={styles.alternativeLabel}>Or copy this link:</Text>
        <div style={styles.urlBox}>
          <Text style={styles.urlText}>{invitation_url}</Text>
        </div>
      </Section>

      {/* Expiration notice */}
      <Section style={styles.expirationNotice}>
        <Text style={styles.expirationText}>
          <strong style={styles.expirationHeading}>
            This invitation expires in {expiration_hours} hours.
          </strong>
          <br />
          After that, you'll need to request a new one.
        </Text>
      </Section>

      {/* Security notice */}
      <Section style={styles.securityNotice}>
        <Text style={styles.securityText}>
          <strong style={styles.securityHeading}>Not expecting this?</strong>
          <br />
          You can safely ignore this email. No action will be taken unless you
          accept the invitation.
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
  inviterName: {
    color: colors.foreground,
    fontWeight: typography.weightSemibold,
  },
  teamName: {
    color: colors.foreground,
    fontWeight: typography.weightSemibold,
  },
  infoCard: {
    backgroundColor: colors.backgroundMuted,
    border: `1px solid ${colors.border}`,
    borderRadius: borderRadius.md,
    padding: spacing.lg,
    marginBottom: spacing.xl,
  },
  infoRow: {
    display: 'flex',
    justifyContent: 'space-between' as const,
    alignItems: 'center' as const,
    padding: `${spacing.sm} 0`,
  },
  dividerLine: {
    height: '1px',
    backgroundColor: colors.border,
    margin: `${spacing.sm} 0`,
  },
  infoLabel: {
    fontSize: '13px',
    color: colors.foregroundSubtle,
    margin: 0,
    fontWeight: typography.weightMedium,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.05em',
  },
  infoValue: {
    fontSize: '15px',
    color: colors.foreground,
    margin: 0,
    fontWeight: typography.weightMedium,
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
  expirationNotice: {
    marginTop: spacing.xl,
    marginBottom: spacing.lg,
    padding: spacing.md,
    backgroundColor: colors.successLight,
    borderRadius: borderRadius.md,
    border: `1px solid ${colors.success}`,
  },
  expirationHeading: {
    color: colors.success,
    fontWeight: typography.weightSemibold,
  },
  expirationText: {
    color: colors.foreground,
    fontSize: '14px',
    lineHeight: typography.lineHeightRelaxed,
    margin: 0,
  },
  securityNotice: {
    marginTop: spacing.lg,
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
