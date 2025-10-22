'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ObjectRelationGroup } from '@/openapi/managerLab.schemas';
import Link from 'next/link';

interface ObjectRelationsProps {
  relations: ObjectRelationGroup[];
  /**
   * Filter to show only specific relation types
   * @example ['parent'] - show only parent relations
   * @example ['child'] - show only child relations
   */
  filter?: ('parent' | 'child')[];
  /**
   * Exclude specific relation names
   * @example ['media'] - exclude media relations (e.g., if showing in a custom gallery)
   */
  exclude?: string[];
}

export function ObjectRelations({
  relations,
  filter,
  exclude = [],
}: ObjectRelationsProps) {
  if (!relations || relations.length === 0) {
    return null;
  }

  // Filter relations based on props
  const filteredRelations = relations.filter((relation) => {
    // Exclude specific relation names
    if (exclude.includes(relation.relation_name)) {
      return false;
    }

    // Filter by relation type if specified
    if (filter && !filter.includes(relation.relation_type)) {
      return false;
    }

    return true;
  });

  if (filteredRelations.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {filteredRelations.map((relation) => (
        <Card key={relation.relation_name}>
          <CardHeader>
            <CardTitle>
              {relation.relation_label}
              {relation.objects.length > 1 && ` (${relation.objects.length})`}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {relation.objects.map((obj) => (
                <div
                  key={obj.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="flex-1">
                    <p className="font-medium">{obj.title}</p>
                    {obj.subtitle && (
                      <p className="text-muted-foreground text-sm">
                        {obj.subtitle}
                      </p>
                    )}
                    <p className="text-muted-foreground text-xs capitalize">
                      {obj.object_type}
                    </p>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/${obj.object_type}/${obj.id}`}>View</Link>
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Legacy exports for backward compatibility (deprecated)
// These will be removed in a future version

interface ObjectParentsProps {
  parents: never[];
}

interface ObjectChildrenProps {
  items: never[];
}

/**
 * @deprecated Use ObjectRelations component with filter={['parent']} instead
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function ObjectParents(_props: ObjectParentsProps) {
  console.warn(
    'ObjectParents is deprecated. Use ObjectRelations with filter={["parent"]} instead.'
  );
  return null;
}

/**
 * @deprecated Use ObjectRelations component with filter={['child']} instead
 */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function ObjectChildren(_props: ObjectChildrenProps) {
  console.warn(
    'ObjectChildren is deprecated. Use ObjectRelations with filter={["child"]} instead.'
  );
  return null;
}
