import { Button as ReactEmailButton } from '@react-email/components';
import * as React from 'react';
import { colors, spacing } from '../design-tokens';

interface ButtonProps {
  href: string;
  children: React.ReactNode;
}

export function Button({ href, children }: ButtonProps) {
  return (
    <ReactEmailButton href={href} style={styles.button}>
      {children}
    </ReactEmailButton>
  );
}

const styles = {
  button: {
    display: 'inline-block',
    padding: `14px 32px`,
    backgroundColor: colors.primary,
    color: colors.primaryForeground,
    textDecoration: 'none',
    borderRadius: '10px',
    fontWeight: 600,
    fontSize: '16px',
    textAlign: 'center' as const,
    cursor: 'pointer',
  },
};
