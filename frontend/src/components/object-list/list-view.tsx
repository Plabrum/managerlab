import { Link } from '@tanstack/react-router';
import { Mail, Instagram, Facebook, Youtube } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  CardRow,
  CardRowAvatar,
  CardRowContent,
  CardRowDescription,
  CardRowLeft,
  CardRowRight,
  CardRowTitle,
} from '@/components/ui/card-row';
import { CardRowList, CardRowListEmpty } from '@/components/ui/card-row-list';
import { Checkbox } from '@/components/ui/checkbox';
import { Image } from '@/components/ui/image';
import { cn } from '@/lib/utils';
import type {
  ObjectListSchema,
  ImageFieldValue,
  ColumnDefinitionSchema,
} from '@/openapi/ariveAPI.schemas';

interface ListViewProps {
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

export function ListView({
  data,
  columns,
  enableRowSelection = false,
  selectedRows,
  onRowSelectionChange,
  onRowClick,
}: ListViewProps) {
  if (!data || data.length === 0) {
    return (
      <CardRowListEmpty
        title="No items to display"
        description="There are no items matching your current filters"
      />
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
      <CardRowList>
        {data.map((item) => {
          const imageField = getImageFromFields(item.fields);
          const imageUrl = imageField?.thumbnail_url || imageField?.url;
          const isSelected = selectedRows.has(item.id);
          const emailValue = emailColumn
            ? getFieldValue(item, emailColumn.key)
            : null;

          return (
            <CardRow
              key={item.id}
              className={cn(isSelected && 'ring-primary ring-2 ring-offset-2')}
            >
              <CardRowLeft>
                {/* Selection checkbox */}
                {enableRowSelection && (
                  <div className="flex items-center">
                    <Checkbox
                      checked={isSelected}
                      onCheckedChange={(checked) =>
                        onRowSelectionChange(item.id, checked === true)
                      }
                      aria-label={`Select ${item.title}`}
                    />
                  </div>
                )}

                {/* Image/Avatar */}
                <CardRowAvatar className="h-16 w-16 overflow-hidden rounded-md">
                  {imageUrl ? (
                    <Image
                      src={imageUrl}
                      alt={item.title}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div
                      className={cn(
                        'flex h-full w-full items-center justify-center',
                        getColorFromString(item.title)
                      )}
                    >
                      <span className="text-lg font-semibold text-white">
                        {getInitials(item.title)}
                      </span>
                    </div>
                  )}
                </CardRowAvatar>

                {/* Content */}
                <CardRowContent>
                  <Link
                    to={item.link || '#'}
                    onClick={(e: React.MouseEvent) => {
                      if (onRowClick) {
                        e.preventDefault();
                        onRowClick(item);
                      }
                    }}
                    className="block"
                  >
                    <CardRowTitle className="hover:text-primary transition-colors">
                      {item.title}
                    </CardRowTitle>
                    {item.subtitle && (
                      <CardRowDescription className="line-clamp-1">
                        {item.subtitle}
                      </CardRowDescription>
                    )}
                  </Link>

                  {/* Email - show on desktop only */}
                  {emailValue && (
                    <CardRowDescription className="mt-1 hidden items-center gap-2 sm:flex">
                      <Mail className="h-3.5 w-3.5 flex-shrink-0 opacity-60" />
                      <span className="truncate">{emailValue}</span>
                    </CardRowDescription>
                  )}
                </CardRowContent>
              </CardRowLeft>

              <CardRowRight>
                {/* Social handles */}
                {socialColumns.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {socialColumns.map((col) => {
                      const value = getFieldValue(item, col.key);
                      if (!value) return null;

                      const Icon =
                        socialIcons[col.key as keyof typeof socialIcons];

                      return (
                        <Badge
                          key={col.key}
                          variant="secondary"
                          className="gap-1.5 text-xs"
                        >
                          {Icon && <Icon className="h-3.5 w-3.5" />}
                          <span className="max-w-[100px] truncate">
                            {value}
                          </span>
                        </Badge>
                      );
                    })}
                  </div>
                )}
              </CardRowRight>
            </CardRow>
          );
        })}
      </CardRowList>
    </div>
  );
}
