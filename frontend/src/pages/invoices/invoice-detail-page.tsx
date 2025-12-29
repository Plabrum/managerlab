import { useParams } from '@tanstack/react-router';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useInvoicesIdGetInvoiceSuspense } from '@/openapi/invoices/invoices';

export function InvoiceDetailPage() {
  const { id } = useParams({ from: '/_authenticated/invoices/$id' });
  const { data, refetch } = useInvoicesIdGetInvoiceSuspense(id);

  return (
    <PageTopBar
      title={`Invoice #${data.invoice_number}`}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.invoice_actions}
          onRefetch={refetch}
        />
      }
    >
      <div className="container mx-auto space-y-6 p-6">
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Customer Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Customer Name
                </label>
                <p className="text-sm">{data.customer_name}</p>
              </div>
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Customer Email
                </label>
                <p className="text-sm">{data.customer_email}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Invoice Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Posting Date
                </label>
                <p className="text-sm">
                  {new Date(data.posting_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Due Date
                </label>
                <p className="text-sm">
                  {new Date(data.due_date).toLocaleDateString()}
                </p>
              </div>
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Amount Due
                </label>
                <p className="text-sm">${data.amount_due.toLocaleString()}</p>
              </div>
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Amount Paid
                </label>
                <p className="text-sm">${data.amount_paid.toLocaleString()}</p>
              </div>
              {data.description && (
                <div>
                  <label className="text-muted-foreground text-sm font-medium">
                    Description
                  </label>
                  <p className="text-sm">{data.description}</p>
                </div>
              )}
              {data.notes && (
                <div>
                  <label className="text-muted-foreground text-sm font-medium">
                    Notes
                  </label>
                  <p className="text-sm">{data.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </PageTopBar>
  );
}
