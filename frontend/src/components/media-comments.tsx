import { formatDistanceToNow } from 'date-fns';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Comment {
  id: string;
  author: {
    name: string;
    avatar?: string;
    initials: string;
  };
  content: string;
  createdAt: Date;
}

interface MediaCommentsProps {
  threadId?: unknown; // TODO: Use for fetching thread comments
}

// Mocked comments data - TODO: Replace with actual thread integration
const MOCK_COMMENTS: Comment[] = [
  {
    id: '1',
    author: {
      name: 'Sarah Johnson',
      initials: 'SJ',
    },
    content: 'Great shot! The lighting is perfect.',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: '2',
    author: {
      name: 'Mike Chen',
      initials: 'MC',
    },
    content: 'Can we get a higher resolution version for the campaign?',
    createdAt: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
  },
  {
    id: '3',
    author: {
      name: 'Emily Davis',
      initials: 'ED',
    },
    content: 'Approved for use in social media posts.',
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
  },
];

export function MediaComments({}: MediaCommentsProps) {
  // TODO: Use threadId to fetch actual comments from the thread
  // For now, using mock data
  const comments = MOCK_COMMENTS;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Comments</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {comments.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No comments yet. Be the first to comment!
            </p>
          ) : (
            comments.map((comment) => (
              <div key={comment.id} className="flex gap-3">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={comment.author.avatar} />
                  <AvatarFallback className="text-xs">
                    {comment.author.initials}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="text-sm font-medium">
                      {comment.author.name}
                    </span>
                    <span className="text-muted-foreground text-xs">
                      {formatDistanceToNow(comment.createdAt, {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                  <p className="text-sm">{comment.content}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
