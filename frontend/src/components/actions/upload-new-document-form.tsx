'use client';

import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Dropzone, DropzoneEmptyState } from '@/components/ui/dropzone';
import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import {
  Loader2,
  UploadIcon,
  CheckCircle2,
  AlertCircle,
  X,
  FileText,
} from 'lucide-react';
import { useDocumentUpload } from '@/hooks/useDocumentUpload';

interface UploadNewDocumentFormProps {
  onSubmit: (documentId: string) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

/**
 * Form for uploading new documents
 * Handles file selection, upload, registration, and calls onSubmit when complete
 */
export function UploadNewDocumentForm({
  onSubmit,
  onCancel,
  isSubmitting = false,
}: UploadNewDocumentFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Use upload hook with callback on success
  const {
    uploadFile,
    status: uploadStatus,
    progress,
    error,
    reset,
  } = useDocumentUpload();

  const handleDrop = useCallback(
    (acceptedFiles: File[]) => {
      const file = acceptedFiles[0];
      if (file) {
        setSelectedFile(file);
        reset();
      }
    },
    [reset]
  );

  const removeFile = () => {
    setSelectedFile(null);
    reset();
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    // Upload with auto-registration and call onSubmit directly on success
    await uploadFile(selectedFile, {
      autoRegister: true,
      onSuccess: (result) => {
        onSubmit(result.documentId);
      },
    });
  };

  const isProcessing =
    uploadStatus === 'uploading' ||
    uploadStatus === 'registering' ||
    isSubmitting;

  // Get file icon based on file type
  const getFileIcon = () => {
    return <FileText className="h-8 w-8" />;
  };

  return (
    <div className="space-y-4">
      {!selectedFile ? (
        <Dropzone
          onDrop={handleDrop}
          accept={{
            'application/pdf': ['.pdf'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
              ['.docx'],
            'application/vnd.ms-excel': ['.xls'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
              ['.xlsx'],
            'text/plain': ['.txt'],
            'text/markdown': ['.md'],
            'text/csv': ['.csv'],
          }}
          maxFiles={1}
          disabled={isProcessing}
        >
          <DropzoneEmptyState>
            <div className="flex flex-col items-center justify-center py-8">
              <div className="bg-muted text-muted-foreground flex size-12 items-center justify-center rounded-md">
                <UploadIcon size={24} />
              </div>
              <p className="my-2 text-lg font-medium">Upload document</p>
              <p className="text-muted-foreground text-sm">
                Drag and drop or click to upload
              </p>
              <p className="text-muted-foreground mt-1 text-xs">
                Accepts PDF, Word, Excel, and text files
              </p>
            </div>
          </DropzoneEmptyState>
        </Dropzone>
      ) : (
        <div className="border-border rounded-lg border p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex min-w-0 flex-1 items-center gap-3">
              <div className="text-muted-foreground flex-shrink-0">
                {getFileIcon()}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">
                  {selectedFile.name}
                </p>
                <p className="text-muted-foreground text-xs">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB •{' '}
                  {selectedFile.type || 'Unknown type'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {uploadStatus === 'uploading' ||
              uploadStatus === 'registering' ? (
                <Loader2 className="text-primary h-4 w-4 animate-spin" />
              ) : uploadStatus === 'complete' ? (
                <CheckCircle2 className="h-4 w-4 text-green-600" />
              ) : uploadStatus === 'error' ? (
                <AlertCircle className="text-destructive h-4 w-4" />
              ) : null}

              {uploadStatus === 'idle' && (
                <Button
                  variant="ghost"
                  size="sm"
                  type="button"
                  onClick={removeFile}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>

          {(uploadStatus === 'uploading' || uploadStatus === 'registering') && (
            <div className="mt-3">
              <Progress value={progress} className="h-2" />
              <p className="text-muted-foreground mt-1 text-xs">
                {uploadStatus === 'uploading'
                  ? 'Uploading to S3...'
                  : 'Registering document...'}
              </p>
            </div>
          )}

          {uploadStatus === 'error' && error && (
            <p className="text-destructive mt-2 text-xs">{error}</p>
          )}

          {uploadStatus === 'complete' && (
            <p className="mt-2 text-xs text-green-600">Upload complete!</p>
          )}
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <Button
          type="button"
          onClick={handleUpload}
          disabled={isProcessing || !selectedFile}
          className="flex-1"
        >
          {isProcessing ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {uploadStatus === 'uploading'
                ? 'Uploading...'
                : uploadStatus === 'registering'
                  ? 'Registering...'
                  : 'Processing...'}
            </>
          ) : (
            'Upload Document'
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isProcessing}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}
