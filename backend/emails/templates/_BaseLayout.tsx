import {
  Body,
  Container,
  Head,
  Html,
  Preview,
  Section,
  Text,
  Hr,
} from '@react-email/components';
import * as React from 'react';
import { colors, typography, spacing } from '../design-tokens';

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
          {/* Header */}
          <Section style={styles.header}>
            <Text style={styles.logo}>Arive</Text>
          </Section>

          {/* Main Content */}
          <Section style={styles.content}>{children}</Section>

          {/* Footer */}
          <Hr style={styles.divider} />
          <Section style={styles.footer}>
            <Text style={styles.footerText}>
              © 2025 Arive. All rights reserved.
            </Text>
            <Text style={styles.footerText}>
              This email was sent from an automated system.
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

const styles = {
  body: {
    backgroundColor: colors.muted,
    fontFamily: typography.fontFamily,
    margin: 0,
    padding: spacing.lg,
  },
  container: {
    backgroundColor: colors.white,
    borderRadius: '10px',
    padding: spacing.xl,
    maxWidth: '600px',
    margin: '0 auto',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
  },
  header: {
    textAlign: 'center' as const,
    paddingBottom: spacing.lg,
    borderBottom: `2px solid ${colors.primary}`,
    marginBottom: spacing.xl,
  },
  logo: {
    fontSize: '32px',
    fontWeight: 700,
    color: colors.primary,
    letterSpacing: '-0.5px',
    margin: 0,
  },
  content: {
    padding: `${spacing.md} 0`,
  },
  divider: {
    borderColor: colors.border,
    margin: `${spacing.xl} 0 ${spacing.lg} 0`,
  },
  footer: {
    textAlign: 'center' as const,
  },
  footerText: {
    fontSize: '13px',
    color: colors.mutedForeground,
    margin: `${spacing.xs} 0`,
    lineHeight: '1.5',
  },
};
