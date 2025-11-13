import {
  Body,
  Container,
  Head,
  Html,
  Preview,
  Section,
  Text,
  Hr,
  Link,
} from '@react-email/components';
import * as React from 'react';
import { colors, typography, spacing, shadows, borderRadius } from '../design-tokens';

interface BaseLayoutProps {
  preview: string;
  children: React.ReactNode;
}

export function BaseLayout({ preview, children }: BaseLayoutProps) {
  return (
    <Html lang="en">
      <Head>
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </Head>
      <Preview>{preview}</Preview>
      <Body style={styles.body}>
        <Container style={styles.container}>
          {/* Minimal Header - just logo, no heavy styling */}
          <Section style={styles.header}>
            <Text style={styles.logo}>Arive</Text>
          </Section>

          {/* Main Content with generous spacing */}
          <Section style={styles.content}>{children}</Section>

          {/* Minimal Footer */}
          <Hr style={styles.divider} />
          <Section style={styles.footer}>
            <Text style={styles.footerText}>
              Sent securely with{' '}
              <Link href="https://tryarive.com" style={styles.footerLink}>
                Arive
              </Link>
            </Text>
            <Text style={styles.footerSubtext}>
              © 2025 Arive. All rights reserved.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const styles = {
  body: {
    backgroundColor: colors.backgroundMuted,
    fontFamily: typography.fontFamily,
    margin: 0,
    padding: `${spacing['2xl']} ${spacing.md}`,
    WebkitFontSmoothing: 'antialiased' as const,
    MozOsxFontSmoothing: 'grayscale' as const,
  },
  container: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: `${spacing['2xl']} ${spacing.xl}`,
    maxWidth: '560px',
    margin: '0 auto',
    boxShadow: shadows.sm,
    border: `1px solid ${colors.borderSubtle}`,
  },
  header: {
    paddingBottom: spacing.xl,
    marginBottom: spacing.xl,
    borderBottom: `1px solid ${colors.borderSubtle}`,
  },
  logo: {
    fontSize: '20px',
    fontWeight: typography.weightSemibold,
    color: colors.foreground,
    letterSpacing: '-0.02em',
    margin: 0,
  },
  content: {
    padding: 0,
  },
  divider: {
    borderColor: colors.borderSubtle,
    margin: `${spacing['2xl']} 0 ${spacing.lg} 0`,
    borderWidth: '1px',
    borderStyle: 'solid',
  },
  footer: {
    textAlign: 'center' as const,
  },
  footerText: {
    fontSize: '13px',
    color: colors.foregroundMuted,
    margin: `${spacing.sm} 0`,
    lineHeight: typography.lineHeightNormal,
    fontWeight: typography.weightNormal,
  },
  footerLink: {
    color: colors.foreground,
    textDecoration: 'none',
    fontWeight: typography.weightMedium,
  },
  footerSubtext: {
    fontSize: '12px',
    color: colors.foregroundSubtle,
    margin: `${spacing.xs} 0 0 0`,
    lineHeight: typography.lineHeightNormal,
  },
};
