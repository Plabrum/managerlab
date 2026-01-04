import React from 'react';
import { UploadIcon, X } from 'lucide-react';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import { Progress } from '@/components/ui/progress';
import { useMediaUpload } from '@/hooks/useMediaUpload';
import { useMediaIdGetMedia } from '@/openapi/media/media';
import { Button } from '../ui/button';
/**
 * Reusable image upload field component
 * Handles file selection, preview, upload to S3, and registration
 */
export function ImageUploadField({
  value,
  onChange,
  maxSizeMB = 10,
}: {
  value?: string | null;
  onChange: (mediaId: string | null) => void;
  maxSizeMB?: number;
}) {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = React.useState<string | null>(null);
  const { uploadFile, status, progress, reset } = useMediaUpload();

  // Fetch existing media when value exists and no file is selected
  const { data: existingMedia } = useMediaIdGetMedia(value ?? '', {
    query: {
      enabled: !!value && !selectedFile,
    },
  });

  const handleDrop = React.useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (!file) return;

      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }

      // Validate file size
      const fileSizeMB = file.size / 1024 / 1024;
      if (fileSizeMB > maxSizeMB) {
        alert(`File size must be less than ${maxSizeMB}MB`);
        return;
      }

      setSelectedFile(file);
      reset();

      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);

      // Upload file
      uploadFile(file, {
        autoRegister: true,
        onSuccess: (result) => {
          onChange(result.mediaId);
        },
      });
    },
    [maxSizeMB, reset, uploadFile, onChange]
  );

  const handleRemove = React.useCallback(() => {
    // Clean up preview URL
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    onChange(null);
    reset();
  }, [previewUrl, onChange, reset]);

  // Clean up preview URL on unmount
  React.useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const isUploading = status === 'uploading' || status === 'registering';

  return (
    <div className="mt-1">
      {!selectedFile && !value ? (
        <Dropzone
          onDrop={handleDrop}
          accept={{
            'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
          }}
          maxFiles={1}
          disabled={isUploading}
        >
          <DropzoneEmptyState>
            <div className="flex flex-col items-center justify-center py-3">
              <div className="bg-muted text-muted-foreground flex size-7 items-center justify-center rounded-md">
                <UploadIcon size={14} />
              </div>
              <p className="my-1 text-sm font-medium">Upload Image</p>
              <p className="text-muted-foreground text-xs">
                Drag and drop or click to upload (max {maxSizeMB}MB)
              </p>
            </div>
          </DropzoneEmptyState>
        </Dropzone>
      ) : (
        <div className="border-border rounded-lg border p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {selectedFile?.name ||
                  existingMedia?.file_name ||
                  'Current image'}
              </p>
              {selectedFile ? (
                <p className="text-muted-foreground text-xs">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              ) : existingMedia ? (
                <p className="text-muted-foreground text-xs">
                  {(existingMedia.file_size / 1024 / 1024).toFixed(2)} MB
                </p>
              ) : null}
            </div>

            {!isUploading && (
              <Button
                variant="ghost"
                size="sm"
                type="button"
                onClick={handleRemove}
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>

          {(previewUrl || existingMedia?.view_url) && (
            <div className="mt-3">
              <img
                src={previewUrl || existingMedia?.view_url}
                alt="Preview"
                className="max-h-32 w-full rounded-md object-contain"
              />
            </div>
          )}

          {status === 'uploading' && (
            <div className="mt-3">
              <Progress value={progress} className="h-2" />
              <p className="text-muted-foreground mt-1 text-xs">
                Uploading... {progress}%
              </p>
            </div>
          )}

          {status === 'registering' && (
            <p className="text-muted-foreground mt-2 text-xs">Processing...</p>
          )}

          {status === 'complete' && (
            <p className="mt-2 text-xs text-green-600">Upload complete!</p>
          )}
        </div>
      )}
    </div>
  );
}
