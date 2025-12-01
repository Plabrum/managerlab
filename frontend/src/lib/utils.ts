import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
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
