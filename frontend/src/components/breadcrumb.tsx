'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  Breadcrumb as BreadcrumbUI,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  campaigns: 'Campaigns',
  brands: 'Brands',
  roster: 'Roster',
  posts: 'Posts',
  media: 'Media',
  invoices: 'Invoices',
  users: 'Users',
  brandcontacts: 'Brand Contacts',
  settings: 'Settings',
  deliverables: 'Deliverables',
};

interface BreadcrumbProps {
  currentPageTitle?: string;
}

export function Breadcrumb({ currentPageTitle }: BreadcrumbProps) {
  const pathname = usePathname();

  // Handle null pathname
  if (!pathname) {
    return null;
  }

  const segments = pathname.split('/').filter(Boolean);

  // Build breadcrumb items
  const breadcrumbItems = segments.map((segment, index) => {
    const path = `/${segments.slice(0, index + 1).join('/')}`;
    const isLast = index === segments.length - 1;

    // For the last segment, use currentPageTitle if provided, otherwise use route label or humanized segment
    const label =
      isLast && currentPageTitle
        ? currentPageTitle
        : routeLabels[segment] ||
          segment.charAt(0).toUpperCase() + segment.slice(1);

    return { path, label, isLast };
  });

  // Don't show breadcrumb if we're at the root
  if (breadcrumbItems.length === 0) {
    return null;
  }

  return (
    <BreadcrumbUI>
      <BreadcrumbList>
        {breadcrumbItems.map((item, index) => (
          <span key={item.path} className="contents">
            <BreadcrumbItem className={index === 0 ? 'hidden md:block' : ''}>
              {item.isLast ? (
                <BreadcrumbPage>{item.label}</BreadcrumbPage>
              ) : (
                <BreadcrumbLink asChild>
                  <Link href={item.path}>{item.label}</Link>
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
            {!item.isLast && (
              <BreadcrumbSeparator className="hidden md:block" />
            )}
          </span>
        ))}
      </BreadcrumbList>
    </BreadcrumbUI>
  );
}
