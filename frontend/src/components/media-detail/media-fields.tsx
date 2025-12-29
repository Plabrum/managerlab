import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { MediaResponseSchema } from '@/openapi/ariveAPI.schemas';

interface MediaFieldsProps {
  media: MediaResponseSchema;
}

export function MediaFields({ media }: MediaFieldsProps) {
  const formatDate = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP p');
    } catch {
      return value;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              File Name
            </dt>
            <dd className="text-sm">{media.file_name}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              File Type
            </dt>
            <dd className="text-sm">{media.file_type}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              File Size
            </dt>
            <dd className="text-sm">{formatFileSize(media.file_size)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              MIME Type
            </dt>
            <dd className="text-sm">{media.mime_type}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Created At
            </dt>
            <dd className="text-sm">{formatDate(media.created_at)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Updated At
            </dt>
            <dd className="text-sm">{formatDate(media.updated_at)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
