import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Get a chart color by index (cycles through 8 chart colors).
 * Colors are defined in globals.css as --color-chart-1 through --color-chart-8.
 *
 * @param index - The index of the color to get (will be modded by 8)
 * @returns CSS color value referencing the CSS variable
 */
export function getChartColor(index: number): string {
  const colorIndex = (index % 8) + 1; // 1-indexed (chart-1 through chart-8)
  return `var(--color-chart-${colorIndex})`;
}
