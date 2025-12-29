/**
 * Helper utilities for creating route meta tags.
 * Use these in TanStack Router's `meta` option for consistent SEO metadata.
 */

export interface MetaTag {
  title?: string;
  name?: string;
  content?: string;
}

/**
 * Create standard meta tags for a page
 */
export function createPageMeta(title: string, description: string): MetaTag[] {
  return [
    { title: `${title} - Arive` },
    { name: 'description', content: description },
  ];
}

/**
 * Create meta tags for a list page (e.g., campaigns, deliverables)
 */
export function createListPageMeta(
  entityName: string,
  action = 'Manage'
): MetaTag[] {
  return createPageMeta(
    entityName,
    `${action} and track all your ${entityName.toLowerCase()}`
  );
}

/**
 * Create meta tags for a detail page
 */
export function createDetailPageMeta(
  entityName: string,
  entityId: string
): MetaTag[] {
  return createPageMeta(
    `${entityName} ${entityId}`,
    `View and manage ${entityName.toLowerCase()} details and activity`
  );
}
