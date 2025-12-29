import { Loader2 } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Image } from '@/components/ui/image';
import { Label } from '@/components/ui/label';
import type {
  ObjectListSchema,
  ImageFieldValue,
} from '@/openapi/ariveAPI.schemas';

interface MediaSelectorProps {
  items: ObjectListSchema[];
  selectedIds: string[];
  onToggle: (mediaId: string, checked: boolean) => void;
  isLoading?: boolean;
  disabled?: boolean;
  emptyMessage?: string;
}

/**
 * Reusable component for selecting media items with checkboxes
 * Displays media thumbnails, titles, and file names
 */
export function MediaSelector({
  items,
  selectedIds,
  onToggle,
  isLoading = false,
  disabled = false,
  emptyMessage = 'No media available.',
}: MediaSelectorProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    );
  }

  if (items.length === 0) {
    return <p className="text-muted-foreground py-4 text-sm">{emptyMessage}</p>;
  }

  return (
    <div className="space-y-2">
      <Label>Select media to add</Label>
      <div className="max-h-96 space-y-3 overflow-y-auto rounded-md border p-4">
        {items.map((media: ObjectListSchema) => {
          const mediaId = String(media.id);
          const isChecked = selectedIds.includes(mediaId);

          // Find image field for thumbnail
          const imageField = media.fields?.find(
            (f) =>
              f.value &&
              typeof f.value === 'object' &&
              'type' in f.value &&
              (f.value as { type: string }).type === 'image'
          );
          const imageValue = imageField?.value as ImageFieldValue | undefined;

          // Find file_name field
          const fileNameField = media.fields?.find(
            (f) => f.key === 'file_name'
          );

          return (
            <div
              key={media.id}
              className="flex items-start gap-3 rounded-md border p-3"
            >
              <Checkbox
                id={`media-${media.id}`}
                checked={isChecked}
                onCheckedChange={(checked) =>
                  onToggle(mediaId, checked === true)
                }
                disabled={disabled}
              />
              <div className="flex flex-1 gap-3">
                {imageValue && (
                  <div className="h-16 w-16 flex-shrink-0 overflow-hidden rounded">
                    <Image
                      src={imageValue.thumbnail_url || imageValue.url}
                      alt={media.title || 'Media thumbnail'}
                      className="h-full w-full object-cover"
                    />
                  </div>
                )}
                <div className="min-w-0 flex-1">
                  <Label
                    htmlFor={`media-${media.id}`}
                    className="cursor-pointer text-sm font-medium"
                  >
                    {media.title || 'Untitled'}
                  </Label>
                  {fileNameField?.value && (
                    <p className="text-muted-foreground mt-1 truncate text-xs">
                      {String(fileNameField.value)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <p className="text-muted-foreground text-xs">
        {selectedIds.length} media item(s) selected
      </p>
    </div>
  );
}
