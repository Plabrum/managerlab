import { Link } from '@tanstack/react-router';
import { Mail, Instagram, Facebook, Youtube } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Image } from '@/components/ui/image';
import { cn } from '@/lib/utils';
import type {
  ObjectListSchema,
  ImageFieldValue,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';

interface CardViewProps {
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

// Helper: Get field value by key
function getFieldValue(row: ObjectListSchema, key: string): string | null {
  const field = row.fields?.find((f) => f.key === key);
  if (!field?.value || typeof field.value !== 'object') return null;
  if ('value' in field.value) {
    const val = field.value.value;
    return typeof val === 'string' ? val : null;
  }
  return null;
}

// Helper: Generate initials from title
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

// Social platform icon mapping
const socialIcons = {
  instagram_handle: Instagram,
  facebook_handle: Facebook,
  tiktok_handle: null, // Lucide doesn't have TikTok icon
  youtube_channel: Youtube,
} as const;

export function CardView({
  data,
  columns,
  enableRowSelection = false,
  selectedRows,
  onRowSelectionChange,
  onRowClick,
}: CardViewProps) {
  if (!data || data.length === 0) {
    return (
      <div className="text-muted-foreground flex h-64 items-center justify-center">
        <p>No items to display</p>
      </div>
    );
  }

  // Find email column
  const emailColumn = columns.find((col) => col.type === 'email');

  // Find social handle columns
  const socialColumns = columns.filter((col) =>
    [
      'instagram_handle',
      'facebook_handle',
      'tiktok_handle',
      'youtube_channel',
    ].includes(col.key)
  );

  return (
    <div className="w-full">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {data.map((item) => {
          const imageField = getImageFromFields(item.fields);
          const imageUrl = imageField?.thumbnail_url || imageField?.url;
          const isSelected = selectedRows.has(item.id);
          const emailValue = emailColumn
            ? getFieldValue(item, emailColumn.key)
            : null;

          return (
            <Card
              key={item.id}
              className={cn(
                'group relative overflow-hidden transition-all hover:shadow-md',
                isSelected && 'ring-primary ring-2 ring-offset-2'
              )}
            >
              {/* Selection checkbox */}
              {enableRowSelection && (
                <div className="absolute right-2 top-2 z-10">
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

              {/* Link wrapper for entire card */}
              <Link
                to={item.link || '#'}
                onClick={(e: React.MouseEvent) => {
                  if (onRowClick) {
                    e.preventDefault();
                    onRowClick(item);
                  }
                }}
                className="block p-2"
              >
                {/* Image or initials */}
                <div className="bg-muted relative aspect-square overflow-hidden rounded-md">
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
                      <span className="text-3xl font-semibold text-white">
                        {getInitials(item.title)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Metadata */}
                <div className="space-y-2 p-4">
                  {/* Title */}
                  <h3 className="truncate font-semibold">{item.title}</h3>

                  {/* Subtitle */}
                  {item.subtitle && (
                    <p className="text-muted-foreground truncate text-xs">
                      {item.subtitle}
                    </p>
                  )}

                  {/* Email */}
                  {emailValue && (
                    <div className="flex items-center gap-2">
                      <Mail className="text-muted-foreground h-3 w-3 shrink-0" />
                      <span className="truncate text-sm">{emailValue}</span>
                    </div>
                  )}

                  {/* Social handles */}
                  {socialColumns.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {socialColumns.map((col) => {
                        const value = getFieldValue(item, col.key);
                        if (!value) return null;

                        const Icon =
                          socialIcons[col.key as keyof typeof socialIcons];

                        return (
                          <Badge
                            key={col.key}
                            variant="secondary"
                            className="gap-1 text-xs"
                          >
                            {Icon && <Icon className="h-3 w-3" />}
                            <span className="max-w-[100px] truncate">
                              {value}
                            </span>
                          </Badge>
                        );
                      })}
                    </div>
                  )}
                </div>
              </Link>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
