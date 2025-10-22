'use client';

import { Card, CardContent } from '@/components/ui/card';
import { ImageOff } from 'lucide-react';

export function EmptyPreview() {
  return (
    <Card className="border-border bg-card w-full max-w-[470px] border">
      <CardContent className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center">
        <div className="bg-muted mb-4 flex h-16 w-16 items-center justify-center rounded-full">
          <ImageOff className="text-muted-foreground h-8 w-8" />
        </div>
        <h3 className="text-foreground mb-2 text-lg font-semibold">
          No Preview Available
        </h3>
        <p className="text-muted-foreground max-w-sm text-sm">
          Approve media to show a preview of how this deliverable will appear on
          the platform.
        </p>
      </CardContent>
    </Card>
  );
}
