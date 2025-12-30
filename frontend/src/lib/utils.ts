import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Maps object types to their corresponding action groups.
 * Returns undefined if the object type doesn't have a corresponding action group.
 *
 * @param objectType - The object type to get the action group for
 * @returns The action group type, or undefined if not found
 */
export function getActionGroupByObjectType(
  objectType: ObjectTypes
): ActionGroupType | undefined {
  const mapping: Partial<Record<ObjectTypes, ActionGroupType>> = {
    campaigns: 'campaign_actions',
    brands: 'brand_actions',
    // TODO: Add brandcontact_actions to backend ActionGroupType enum
    // brandcontacts: 'brandcontact_actions',
    deliverables: 'deliverable_actions',
    invoices: 'invoice_actions',
    media: 'media_actions',
    roster: 'roster_actions',
    // TODO: Add user_actions to backend ActionGroupType enum
    // users: 'user_actions',
  };

  return mapping[objectType];
}

/**
 * Get a chart color by index (cycles through 9 chart colors).
 * Colors are defined in globals.css as --color-chart-1 through --color-chart-9.
 *
 * @param index - The index of the color to get (will be modded by 9)
 * @returns CSS color value referencing the CSS variable
 */
export function getChartColor(index: number): string {
  const colorIndex = (index % 9) + 1; // 1-indexed (chart-1 through chart-9)
  return `var(--color-chart-${colorIndex})`;
}
