'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Image } from '@/components/ui/image';
import type {
  ObjectListDTO,
  ImageFieldValue,
} from '@/openapi/managerLab.schemas';
import Link from 'next/link';

interface MediaGalleryProps {
  items: ObjectListDTO[];
}

function getImageFromFields(
  fields: ObjectListDTO['fields']
): ImageFieldValue | null {
  if (!fields) return null;

  for (const field of fields) {
    if (
      field.value &&
      typeof field.value === 'object' &&
      'type' in field.value
    ) {
      if (field.value.type === 'image') {
        return field.value as ImageFieldValue;
      }
    }
  }

  return null;
}

export function MediaGallery({ items }: MediaGalleryProps) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Media ({items.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {items.map((media) => {
            const imageField = getImageFromFields(media.fields);
            const imageUrl = imageField?.thumbnail_url || imageField?.url;

            return (
              <Link
                key={media.id}
                href={`/${media.object_type}/${media.id}`}
                className="bg-muted hover:border-primary group relative aspect-square overflow-hidden rounded-lg border transition-all hover:shadow-md"
              >
                {imageUrl ? (
                  <Image
                    src={imageUrl}
                    alt={media.title}
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                ) : (
                  <div className="text-muted-foreground flex h-full w-full items-center justify-center">
                    <span className="px-2 text-center text-xs">
                      {media.title}
                    </span>
                  </div>
                )}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                  <p className="truncate text-xs text-white">{media.title}</p>
                </div>
              </Link>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
