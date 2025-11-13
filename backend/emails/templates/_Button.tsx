import { Button as ReactEmailButton } from '@react-email/components';
import * as React from 'react';

interface ButtonProps {
  href: string;
  children: React.ReactNode;
}

export function Button({ href, children }: ButtonProps) {
  return (
    <ReactEmailButton
      href={href}
      className="inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-neutral-950 text-white no-underline rounded-full font-medium text-[15px] text-center cursor-pointer border-none leading-tight"
    >
      <span className="inline-block">{children}</span>
      <span className="inline-block text-base leading-none ml-1">→</span>
    </ReactEmailButton>
  );
}
