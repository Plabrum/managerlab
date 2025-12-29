import { Link } from '@tanstack/react-router';
import type React from 'react';

interface FooterLinkProps {
  href: string;
  children: React.ReactNode;
  external?: boolean;
}

export function FooterLink({
  href,
  children,
  external = false,
}: FooterLinkProps) {
  if (external) {
    return (
      <li>
        <a
          href={href}
          className="hover:text-foreground transition-colors"
          target="_blank"
          rel="noopener noreferrer"
        >
          {children}
        </a>
      </li>
    );
  }

  return (
    <li>
      <Link to={href} className="hover:text-foreground transition-colors">
        {children}
      </Link>
    </li>
  );
}
