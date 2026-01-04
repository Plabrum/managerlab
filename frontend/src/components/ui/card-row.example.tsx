/**
 * CardRow Component Usage Examples
 *
 * This file demonstrates how to use the CardRow component system
 * for creating horizontal list items with consistent styling.
 */

import { Mail, Settings, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  CardRow,
  CardRowAvatar,
  CardRowContent,
  CardRowDescription,
  CardRowLeft,
  CardRowRight,
  CardRowTitle,
} from '@/components/ui/card-row';
import {
  CardRowList,
  CardRowListEmpty,
  CardRowListHeader,
} from '@/components/ui/card-row-list';

// ============================================================================
// Example 1: Basic Usage
// ============================================================================
export function BasicCardRowExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="Basic Example"
        description="A simple card row with title and description"
      />

      <CardRowList>
        <CardRow>
          <CardRowLeft>
            <CardRowContent>
              <CardRowTitle>Simple Title</CardRowTitle>
              <CardRowDescription>
                This is a basic description
              </CardRowDescription>
            </CardRowContent>
          </CardRowLeft>

          <CardRowRight>
            <Badge>Active</Badge>
          </CardRowRight>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 2: With Avatar
// ============================================================================
export function CardRowWithAvatarExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="With Avatar"
        description="Card rows with avatars and initials"
      />

      <CardRowList>
        <CardRow>
          <CardRowLeft>
            <CardRowAvatar>
              <span className="text-primary text-base font-semibold">JD</span>
            </CardRowAvatar>

            <CardRowContent>
              <CardRowTitle>John Doe</CardRowTitle>
              <CardRowDescription>
                <div className="flex items-center gap-2">
                  <Mail className="h-3.5 w-3.5" />
                  john@example.com
                </div>
              </CardRowDescription>
            </CardRowContent>
          </CardRowLeft>

          <CardRowRight>
            <Badge>Admin</Badge>
          </CardRowRight>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 3: With Icon Avatar
// ============================================================================
export function CardRowWithIconExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="With Icons"
        description="Using icons instead of initials"
      />

      <CardRowList>
        <CardRow>
          <CardRowLeft>
            <CardRowAvatar>
              <User className="text-primary h-5 w-5" />
            </CardRowAvatar>

            <CardRowContent>
              <CardRowTitle>User Settings</CardRowTitle>
              <CardRowDescription>
                Manage your account preferences
              </CardRowDescription>
            </CardRowContent>
          </CardRowLeft>

          <CardRowRight>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </CardRowRight>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 4: Clickable Rows
// ============================================================================
export function ClickableCardRowExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="Clickable Rows"
        description="Rows that respond to clicks"
      />

      <CardRowList>
        <CardRow onClick={() => console.log('Row clicked!')}>
          <CardRowLeft>
            <CardRowContent>
              <CardRowTitle>Click me!</CardRowTitle>
              <CardRowDescription>This row is interactive</CardRowDescription>
            </CardRowContent>
          </CardRowLeft>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 5: Empty State
// ============================================================================
export function EmptyStateExample() {
  const items: never[] = [];

  return (
    <div className="p-8">
      <CardRowListHeader
        title="Empty State"
        description="Showing when there are no items"
      />

      {items.length === 0 ? (
        <CardRowListEmpty
          title="No items found"
          description="Add your first item to get started"
        />
      ) : (
        <CardRowList>
          {items.map((item) => (
            <CardRow key={item}>
              <CardRowLeft>
                <CardRowContent>
                  <CardRowTitle>Item</CardRowTitle>
                </CardRowContent>
              </CardRowLeft>
            </CardRow>
          ))}
        </CardRowList>
      )}
    </div>
  );
}

// ============================================================================
// Example 6: With Header Actions
// ============================================================================
export function CardRowWithHeaderActionsExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="With Actions"
        description="Header with action buttons"
        actions={
          <Button size="sm" variant="default">
            Add New
          </Button>
        }
      />

      <CardRowList>
        <CardRow>
          <CardRowLeft>
            <CardRowContent>
              <CardRowTitle>Item 1</CardRowTitle>
              <CardRowDescription>Description</CardRowDescription>
            </CardRowContent>
          </CardRowLeft>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 7: Custom Styling
// ============================================================================
export function CustomStyledCardRowExample() {
  return (
    <div className="p-8">
      <CardRowListHeader title="Custom Styling" />

      <CardRowList className="space-y-4">
        {' '}
        {/* Increased spacing */}
        <CardRow className="border-l-4 border-l-blue-500 bg-blue-50/50">
          <CardRowLeft>
            <CardRowContent>
              <CardRowTitle className="text-blue-900">
                Custom Styled Row
              </CardRowTitle>
              <CardRowDescription className="text-blue-700">
                With custom colors and border
              </CardRowDescription>
            </CardRowContent>
          </CardRowLeft>
        </CardRow>
      </CardRowList>
    </div>
  );
}

// ============================================================================
// Example 8: Complex Multi-Badge Layout
// ============================================================================
export function ComplexCardRowExample() {
  return (
    <div className="p-8">
      <CardRowListHeader
        title="Complex Layout"
        description="Multiple badges and metadata"
      />

      <CardRowList>
        <CardRow>
          <CardRowLeft>
            <CardRowAvatar>
              <span className="text-primary text-base font-semibold">AC</span>
            </CardRowAvatar>

            <CardRowContent>
              <CardRowTitle>ACME Corporation</CardRowTitle>
              <CardRowDescription>
                <div className="flex items-center gap-2">
                  <Mail className="h-3.5 w-3.5" />
                  contact@acme.com
                </div>
              </CardRowDescription>
            </CardRowContent>
          </CardRowLeft>

          <CardRowRight>
            <Badge variant="outline">Enterprise</Badge>
            <Badge variant="secondary">Active</Badge>
            <Badge variant="default">Premium</Badge>
            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </CardRowRight>
        </CardRow>
      </CardRowList>
    </div>
  );
}
