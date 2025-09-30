'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type {
  ObjectDetailDTOParentsItem,
  ObjectDetailDTOChildrenItem,
} from '@/openapi/managerLab.schemas';

interface ObjectParentsProps {
  parents: ObjectDetailDTOParentsItem[];
}

interface ObjectChildrenProps {
  items: ObjectDetailDTOChildrenItem[];
}

export function ObjectParents({ parents }: ObjectParentsProps) {
  if (!parents || parents.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Related Objects</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {parents.map((parent, index) => {
            const [, relation] = Object.entries(parent)[0];
            return (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div>
                  <p className="font-medium">{relation.title}</p>
                  <p className="text-muted-foreground text-sm">
                    {relation.object_type}
                  </p>
                </div>
                <Button variant="ghost" size="sm" asChild>
                  <a href={`/${relation.object_type}/${relation.sqid}`}>View</a>
                </Button>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

export function ObjectChildren({ items }: ObjectChildrenProps) {
  if (!items || items.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Child Objects</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {items.map((child, index) => {
            const [, relation] = Object.entries(child)[0];
            return (
              <div
                key={index}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div>
                  <p className="font-medium">{relation.title}</p>
                  <p className="text-muted-foreground text-sm">
                    {relation.object_type}
                  </p>
                </div>
                <Button variant="ghost" size="sm" asChild>
                  <a href={`/${relation.object_type}/${relation.sqid}`}>View</a>
                </Button>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
