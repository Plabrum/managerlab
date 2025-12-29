import { Image } from '@/components/ui/image';
import { cn } from '@/lib/utils';
import type { MediaResponseSchema } from '@/openapi/ariveAPI.schemas';

interface SimpleMediaGalleryProps {
  media: MediaResponseSchema[];
  selectedIndex?: number;
  onMediaSelect?: (index: number) => void;
}

export function SimpleMediaGallery({
  media,
  selectedIndex,
  onMediaSelect,
}: SimpleMediaGalleryProps) {
  if (!media || media.length === 0) {
    return null;
  }

  return (
    <div className="w-full">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {media.map((item, index) => {
          const imageUrl = item.thumbnail_url || item.view_url;
          const mediaId = item.id as string;
          const isSelected = selectedIndex === index;

          return (
            <button
              key={mediaId}
              type="button"
              onClick={() => onMediaSelect?.(index)}
              className={cn(
                'bg-muted hover:border-primary group relative aspect-square overflow-hidden rounded-lg border transition-all hover:shadow-md',
                isSelected &&
                  'ring-primary border-primary shadow-lg ring-2 ring-offset-2'
              )}
            >
              {imageUrl ? (
                <Image
                  src={imageUrl}
                  alt={item.file_name}
                  className="h-full w-full object-cover transition-transform group-hover:scale-105"
                />
              ) : (
                <div className="text-muted-foreground flex h-full w-full items-center justify-center">
                  <span className="px-2 text-center text-xs">
                    {item.file_name}
                  </span>
                </div>
              )}
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                <p className="truncate text-xs text-white">{item.file_name}</p>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
