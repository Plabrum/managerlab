'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { useBreadcrumb } from '@/components/breadcrumb-provider';

interface DetailPageLayoutProps {
  children: React.ReactNode;
  objectTitle: string | null | undefined;
}

export function DetailPageLayout({
  children,
  objectTitle,
}: DetailPageLayoutProps) {
  const pathname = usePathname();
  const { setBreadcrumb, clearBreadcrumb } = useBreadcrumb();

  // Set breadcrumb title when data loads
  useEffect(() => {
    setBreadcrumb(pathname, objectTitle);
    return () => {
      clearBreadcrumb(pathname);
    };
  }, [objectTitle, pathname, setBreadcrumb, clearBreadcrumb]);

  return <>{children}</>;
}
