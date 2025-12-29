import { Link } from '@tanstack/react-router';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

// Type definitions for object relations
// TODO: These types are temporary - remove when relations are properly implemented
interface RelationObject {
  id: string;
  title: string;
  subtitle?: string | null;
  state?: string | null;
  url: string;
  object_type: string;
}

interface ObjectRelationGroup {
  relation_name: string;
  relation_label: string;
  relation_type: 'parent' | 'child';
  objects: RelationObject[];
}

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
                    <Link to={`/${obj.object_type}/${obj.id}`}>View</Link>
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

/**
 * @deprecated Use ObjectRelations component with filter={['parent']} instead
 */
export function ObjectParents() {
  console.warn(
    'ObjectParents is deprecated. Use ObjectRelations with filter={["parent"]} instead.'
  );
  return null;
}

/**
 * @deprecated Use ObjectRelations component with filter={['child']} instead
 */
export function ObjectChildren() {
  console.warn(
    'ObjectChildren is deprecated. Use ObjectRelations with filter={["child"]} instead.'
  );
  return null;
}
