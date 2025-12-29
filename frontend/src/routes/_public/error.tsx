import { createFileRoute, Link, useRouter } from '@tanstack/react-router';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export const Route = createFileRoute('/_public/error')({
  component: ErrorPage,
});

function ErrorPage() {
  const router = useRouter();

  return (
    <div className="bg-background flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="bg-destructive/10 mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full">
            <AlertCircle className="text-destructive h-6 w-6" />
          </div>
          <CardTitle className="text-2xl">Something went wrong</CardTitle>
          <CardDescription>
            We encountered an unexpected error. Our team has been notified and
            we&apos;re working on it. Please try again or contact support if the
            problem persists.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-muted text-muted-foreground rounded-lg p-4 text-sm">
            <p className="font-medium">Error Code: 500</p>
            <p className="mt-1">Internal Server Error</p>
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-2">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => router.history.back()}
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Try Again
          </Button>
          <Button asChild className="w-full">
            <Link to="/auth/expire">
              <AlertCircle className="mr-2 h-4 w-4" />
              Re-authenticate
            </Link>
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
}

export default ErrorPage;
