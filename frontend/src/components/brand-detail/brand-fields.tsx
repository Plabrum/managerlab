'use client';

import { format } from 'date-fns';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { BrandSchema } from '@/openapi/ariveAPI.schemas';

interface BrandFieldsProps {
  brand: BrandSchema;
}

export function BrandFields({ brand }: BrandFieldsProps) {
  const formatDate = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP p');
    } catch {
      return value;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {brand.description && (
            <div className="space-y-1 sm:col-span-2">
              <dt className="text-muted-foreground text-sm font-medium">
                Description
              </dt>
              <dd className="text-sm">{brand.description}</dd>
            </div>
          )}

          {brand.website && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Website
              </dt>
              <dd className="text-sm">
                <a
                  href={brand.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  {brand.website}
                </a>
              </dd>
            </div>
          )}

          {brand.email && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Email
              </dt>
              <dd className="text-sm">
                <a
                  href={`mailto:${brand.email}`}
                  className="text-primary hover:underline"
                >
                  {brand.email}
                </a>
              </dd>
            </div>
          )}

          {brand.phone && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Phone
              </dt>
              <dd className="text-sm">
                <a
                  href={`tel:${brand.phone}`}
                  className="text-primary hover:underline"
                >
                  {brand.phone}
                </a>
              </dd>
            </div>
          )}

          {brand.notes && (
            <div className="space-y-1 sm:col-span-2">
              <dt className="text-muted-foreground text-sm font-medium">
                Notes
              </dt>
              <dd className="whitespace-pre-wrap text-sm">{brand.notes}</dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Created At
            </dt>
            <dd className="text-sm">{formatDate(brand.created_at)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Updated At
            </dt>
            <dd className="text-sm">{formatDate(brand.updated_at)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
