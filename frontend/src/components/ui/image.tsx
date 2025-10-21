import { forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface ImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  /**
   * Alternative text for the image
   */
  alt: string;
  /**
   * Image source URL
   */
  src: string;
}

/**
 * A simple image wrapper component that provides consistent styling
 * and suppresses Next.js ESLint warnings in one place.
 *
 * Note: This component uses native <img> instead of next/image for cases where:
 * - Images are user-uploaded content from external URLs
 * - We need full control over loading behavior
 * - Dynamic aspect ratios are required
 *
 * For static assets or when optimization is critical, consider using next/image directly.
 */
const Image = forwardRef<HTMLImageElement, ImageProps>(
  ({ className, alt, src, ...props }, ref) => {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img ref={ref} src={src} alt={alt} className={cn(className)} {...props} />
    );
  }
);

Image.displayName = 'Image';

export { Image };
