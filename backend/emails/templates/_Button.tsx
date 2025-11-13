import { Button as ReactEmailButton } from '@react-email/components';
import * as React from 'react';
import { colors, spacing, borderRadius, typography } from '../design-tokens';

interface ButtonProps {
  href: string;
  children: React.ReactNode;
}

export function Button({ href, children }: ButtonProps) {
  return (
    <ReactEmailButton href={href} style={styles.button}>
      <span style={styles.buttonText}>{children}</span>
      <span style={styles.arrow}>→</span>
    </ReactEmailButton>
  );
}

const styles = {
  button: {
    display: 'inline-flex' as const,
    alignItems: 'center' as const,
    justifyContent: 'center' as const,
    gap: spacing.sm,
    padding: `14px 28px`,
    background: `linear-gradient(180deg, ${colors.gradientFrom} 0%, ${colors.gradientTo} 100%)`,
    color: colors.primaryForeground,
    textDecoration: 'none',
    borderRadius: borderRadius.full,
    fontWeight: typography.weightMedium,
    fontSize: '15px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    border: 'none',
    lineHeight: typography.lineHeightTight,
    transition: 'all 0.2s ease',
  },
  buttonText: {
    display: 'inline-block',
  },
  arrow: {
    display: 'inline-block',
    fontSize: '16px',
    lineHeight: '1',
    marginLeft: spacing.xs,
  },
};
