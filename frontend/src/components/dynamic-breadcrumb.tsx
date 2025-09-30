'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { useBreadcrumb } from '@/components/breadcrumb-provider';

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
};

export function DynamicBreadcrumb() {
  const pathname = usePathname();
  const { breadcrumbs } = useBreadcrumb();
  const segments = pathname.split('/').filter(Boolean);

  // Remove empty segments and build breadcrumb items
  const breadcrumbItems = segments.map((segment, index) => {
    const path = `/${segments.slice(0, index + 1).join('/')}`;

    // Check if there's a custom breadcrumb override for this path
    const customLabel = breadcrumbs.get(path);
    const label =
      customLabel ||
      routeLabels[segment] ||
      segment.charAt(0).toUpperCase() + segment.slice(1);
    const isLast = index === segments.length - 1;

    return { path, label, isLast };
  });

  // Don't show breadcrumb if we're at the root
  if (breadcrumbItems.length === 0) {
    return null;
  }

  return (
    <Breadcrumb>
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
    </Breadcrumb>
  );
}
