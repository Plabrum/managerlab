'use client';

import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Image } from '@/components/ui/image';
import type {
  ObjectFieldDTO,
  ObjectFieldDTOValue,
} from '@/openapi/managerLab.schemas';

interface ObjectFieldsProps {
  fields: ObjectFieldDTO[];
}

export function ObjectFields({ fields }: ObjectFieldsProps) {
  const renderFieldValue = (field: ObjectFieldDTO) => {
    const value = field.value;

    if (value === null || value === undefined) {
      return <span className="text-muted-foreground">—</span>;
    }

    // Handle discriminated union field values
    if (typeof value === 'object' && value !== null && 'type' in value) {
      const fieldValue = value as NonNullable<ObjectFieldDTOValue>;
      const fieldType = fieldValue.type;

      switch (fieldType) {
        case 'image':
          if (fieldValue.url) {
            return (
              <div className="flex items-center gap-2">
                <Image
                  src={fieldValue.thumbnail_url || fieldValue.url}
                  alt="Image"
                  className="h-24 w-24 rounded object-cover"
                />
                <a
                  href={fieldValue.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary text-sm hover:underline"
                >
                  View full size
                </a>
              </div>
            );
          }
          return <span className="text-muted-foreground">—</span>;

        case 'date':
          if (fieldValue.value) {
            return format(new Date(fieldValue.value), 'PPP');
          }
          return <span className="text-muted-foreground">—</span>;

        case 'datetime':
          if (fieldValue.value) {
            return format(new Date(fieldValue.value), 'PPP p');
          }
          return <span className="text-muted-foreground">—</span>;

        case 'bool':
          return (
            <Badge variant={fieldValue.value ? 'default' : 'secondary'}>
              {fieldValue.value ? 'Yes' : 'No'}
            </Badge>
          );

        case 'email':
          if (fieldValue.value) {
            return (
              <a
                href={`mailto:${fieldValue.value}`}
                className="text-primary hover:underline"
              >
                {String(fieldValue.value)}
              </a>
            );
          }
          return <span className="text-muted-foreground">—</span>;

        case 'url':
          if (fieldValue.value) {
            return (
              <a
                href={String(fieldValue.value)}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline"
              >
                {fieldValue.label || String(fieldValue.value)}
              </a>
            );
          }
          return <span className="text-muted-foreground">—</span>;

        case 'usd':
          return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
          }).format(Number(fieldValue.value));

        case 'enum':
          return <Badge variant="outline">{String(fieldValue.value)}</Badge>;

        case 'string':
        case 'text':
        case 'int':
        case 'float':
        default:
          return String(fieldValue.value || '');
      }
    }

    // Fallback for backwards compatibility
    return String(value);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {fields.map((field) => (
            <div key={field.key} className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                {field.label || field.key}
              </dt>
              <dd className="text-sm">{renderFieldValue(field)}</dd>
            </div>
          ))}
        </dl>
      </CardContent>
    </Card>
  );
}
