'use client';

import { Image } from '@/components/ui/image';
import { Checkbox } from '@/components/ui/checkbox';
import type {
  ObjectListSchema,
  ImageFieldValue,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';
import Link from 'next/link';
import { cn } from '@/lib/utils';

interface GalleryViewProps {
  data: ObjectListSchema[];
  columns: ColumnDefinitionSchema[];
  enableRowSelection?: boolean;
  selectedRows: Set<string>;
  onRowSelectionChange: (rowId: string, selected: boolean) => void;
  onRowClick?: (row: ObjectListSchema) => void;
}

// Helper: Extract image field value from ObjectListSchema fields
function getImageFromFields(
  fields: ObjectListSchema['fields']
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

// Helper: Generate initials from title (first letter of each word, max 2)
function getInitials(title: string): string {
  return title
    .split(' ')
    .map((word) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// Helper: Generate consistent color from string hash
function getColorFromString(str: string): string {
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-red-500',
    'bg-purple-500',
    'bg-pink-500',
    'bg-indigo-500',
    'bg-teal-500',
  ];
  const hash = str.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
}

export function GalleryView({
  data,
  enableRowSelection = false,
  selectedRows,
  onRowSelectionChange,
  onRowClick,
}: GalleryViewProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-muted-foreground flex h-64 items-center justify-center">
        <p>No items to display</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
        {data.map((item) => {
          const imageField = getImageFromFields(item.fields);
          const imageUrl = imageField?.thumbnail_url || imageField?.url;
          const isSelected = selectedRows.has(item.id);

          return (
            <div key={item.id} className="group relative aspect-square">
              {/* Selection checkbox */}
              {enableRowSelection && (
                <div
                  className={cn(
                    'absolute left-2 top-2 z-10 transition-opacity',
                    isSelected
                      ? 'opacity-100'
                      : 'opacity-0 group-hover:opacity-100'
                  )}
                >
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={(checked) =>
                      onRowSelectionChange(item.id, checked === true)
                    }
                    aria-label={`Select ${item.title}`}
                    className="bg-background border-2"
                  />
                </div>
              )}

              {/* Link wrapper */}
              <Link
                href={item.link || '#'}
                onClick={(e) => {
                  if (onRowClick) {
                    e.preventDefault();
                    onRowClick(item);
                  }
                }}
                className={cn(
                  'bg-muted hover:border-primary block h-full w-full overflow-hidden rounded-lg border transition-all hover:shadow-md',
                  isSelected && 'ring-primary ring-2 ring-offset-2'
                )}
              >
                {/* Image or initials */}
                {imageUrl ? (
                  <Image
                    src={imageUrl}
                    alt={item.title}
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                ) : (
                  <div
                    className={cn(
                      'flex h-full w-full items-center justify-center',
                      getColorFromString(item.title)
                    )}
                  >
                    <span className="text-2xl font-semibold text-white">
                      {getInitials(item.title)}
                    </span>
                  </div>
                )}

                {/* Hover overlay with title */}
                <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-2 opacity-0 transition-opacity group-hover:opacity-100">
                  <p className="truncate text-xs font-medium text-white">
                    {item.title}
                  </p>
                  {item.subtitle && (
                    <p className="truncate text-xs text-white/80">
                      {item.subtitle}
                    </p>
                  )}
                </div>
              </Link>
            </div>
          );
        })}
      </div>
    </div>
  );
}
