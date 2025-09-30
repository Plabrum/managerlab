/**
 * Humanize an enum value by replacing underscores with spaces and capitalizing
 * @example humanizeEnumValue('active_user') => 'Active user'
 */
export function humanizeEnumValue(value: string): string {
  const normalized = value.replace(/_/g, ' ').toLowerCase();
  return normalized.charAt(0).toUpperCase() + normalized.slice(1);
}
