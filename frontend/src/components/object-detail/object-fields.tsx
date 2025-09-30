'use client';

import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ObjectFieldDTO } from '@/openapi/managerLab.schemas';

interface ObjectFieldsProps {
  fields: ObjectFieldDTO[];
}

export function ObjectFields({ fields }: ObjectFieldsProps) {
  const renderFieldValue = (field: ObjectFieldDTO) => {
    const { value, type } = field;

    if (value === null || value === undefined) {
      return <span className="text-muted-foreground">—</span>;
    }

    switch (type) {
      case 'date':
        return format(new Date(value as string), 'PPP');
      case 'datetime':
        return format(new Date(value as string), 'PPP p');
      case 'bool':
        return (
          <Badge variant={value ? 'default' : 'secondary'}>
            {value ? 'Yes' : 'No'}
          </Badge>
        );
      case 'email':
        return (
          <a href={`mailto:${value}`} className="text-primary hover:underline">
            {String(value)}
          </a>
        );
      case 'url':
        return (
          <a
            href={String(value)}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline"
          >
            {String(value)}
          </a>
        );
      case 'usd':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
        }).format(Number(value));
      case 'enum':
        return <Badge variant="outline">{String(value)}</Badge>;
      default:
        return String(value);
    }
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
