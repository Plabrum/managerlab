import type React from 'react';
interface FooterLinkProps {
  href: string;
  children: React.ReactNode;
}

export function FooterLink({ href, children }: FooterLinkProps) {
  return (
    <li>
      <a href={href} className="hover:text-foreground transition-colors">
        {children}
      </a>
    </li>
  );
}
