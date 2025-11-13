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
  Tailwind,
  Button as ReactEmailButton,
} from '@react-email/components';
import * as React from 'react';

interface BaseLayoutProps {
  preview: string;
  children: React.ReactNode;
}

export function BaseLayout({ preview, children }: BaseLayoutProps) {
  return (
    <Html lang="en">
      <Tailwind>
        <Head />
        <Preview>{preview}</Preview>
        <Body className="bg-white md:bg-neutral-50 font-sans m-0 md:py-12 md:px-4 antialiased">
          <Container className="bg-white md:rounded-xl p-4 md:p-12 max-w-[560px] mx-auto md:shadow-sm md:border md:border-neutral-100">
            {/* Minimal Header - just logo, no heavy styling */}
            <Section className="pb-6 md:pb-8 mb-6 md:mb-8 border-b border-neutral-100">
              <Text className="text-xl font-semibold text-foreground tracking-tight m-0">
                Arive
              </Text>
            </Section>

            {/* Main Content with generous spacing */}
            <Section className="p-0">{children}</Section>

            {/* Minimal Footer */}
            <Hr className="border-neutral-100 my-8 md:my-12 mb-4 md:mb-6" />
            <Section className="text-center">
              <Text className="text-[13px] text-muted-foreground my-2 leading-normal font-normal">
                Sent securely with{' '}
                <Link
                  href="https://tryarive.com"
                  className="text-foreground no-underline font-medium"
                >
                  Arive
                </Link>
              </Text>
              <Text className="text-xs text-neutral-400 mt-1 mb-0 leading-normal">
                © 2025 Arive. All rights reserved.
              </Text>
            </Section>
          </Container>
        </Body>
      </Tailwind>
    </Html>
  );
}

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
