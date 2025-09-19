import type { ReactNode } from 'react';

interface FooterSectionProps {
  title: string;
  children: ReactNode;
}

export function FooterSection({ title, children }: FooterSectionProps) {
  return (
    <div className="space-y-4">
      <h4 className="font-semibold">{title}</h4>
      <ul className="text-muted-foreground space-y-2 text-sm">{children}</ul>
    </div>
  );
}
