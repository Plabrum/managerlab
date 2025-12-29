import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { CampaignSchema } from '@/openapi/ariveAPI.schemas';

interface CampaignFieldsProps {
  campaign: CampaignSchema;
}

export function CampaignFields({ campaign }: CampaignFieldsProps) {
  const formatCurrency = (value: number | null | undefined) => {
    if (value === null || value === undefined) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatDate = (value: string | null | undefined) => {
    if (!value) return '—';
    try {
      return format(new Date(value), 'PPP');
    } catch {
      return value;
    }
  };

  const formatValue = (value: unknown) => {
    if (value === null || value === undefined) return '—';
    return String(value);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Details</CardTitle>
      </CardHeader>
      <CardContent>
        <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
          {campaign.description && (
            <div className="space-y-1 sm:col-span-2">
              <dt className="text-muted-foreground text-sm font-medium">
                Description
              </dt>
              <dd className="text-sm">{campaign.description}</dd>
            </div>
          )}

          {campaign.counterparty_type && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Counterparty Type
              </dt>
              <dd className="text-sm">
                <Badge variant="outline">{campaign.counterparty_type}</Badge>
              </dd>
            </div>
          )}

          {campaign.counterparty_name && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Counterparty Name
              </dt>
              <dd className="text-sm">{campaign.counterparty_name}</dd>
            </div>
          )}

          {campaign.counterparty_email && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Counterparty Email
              </dt>
              <dd className="text-sm">
                <a
                  href={`mailto:${campaign.counterparty_email}`}
                  className="text-primary hover:underline"
                >
                  {campaign.counterparty_email}
                </a>
              </dd>
            </div>
          )}

          {campaign.compensation_structure && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Compensation Structure
              </dt>
              <dd className="text-sm">
                <Badge variant="outline">
                  {campaign.compensation_structure}
                </Badge>
              </dd>
            </div>
          )}

          {campaign.compensation_total_usd !== null &&
            campaign.compensation_total_usd !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Total Compensation
                </dt>
                <dd className="text-sm font-semibold">
                  {formatCurrency(campaign.compensation_total_usd)}
                </dd>
              </div>
            )}

          {campaign.payment_terms_days !== null &&
            campaign.payment_terms_days !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Payment Terms
                </dt>
                <dd className="text-sm">{campaign.payment_terms_days} days</dd>
              </div>
            )}

          {campaign.flight_start_date && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Flight Start Date
              </dt>
              <dd className="text-sm">
                {formatDate(campaign.flight_start_date)}
              </dd>
            </div>
          )}

          {campaign.flight_end_date && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Flight End Date
              </dt>
              <dd className="text-sm">
                {formatDate(campaign.flight_end_date)}
              </dd>
            </div>
          )}

          {campaign.ftc_string && (
            <div className="space-y-1 sm:col-span-2">
              <dt className="text-muted-foreground text-sm font-medium">
                FTC Disclosure
              </dt>
              <dd className="text-sm">{campaign.ftc_string}</dd>
            </div>
          )}

          {campaign.usage_duration && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Usage Duration
              </dt>
              <dd className="text-sm">{campaign.usage_duration}</dd>
            </div>
          )}

          {campaign.usage_territory && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Usage Territory
              </dt>
              <dd className="text-sm">{campaign.usage_territory}</dd>
            </div>
          )}

          {campaign.usage_paid_media_option !== null &&
            campaign.usage_paid_media_option !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Paid Media Option
                </dt>
                <dd className="text-sm">
                  <Badge
                    variant={
                      campaign.usage_paid_media_option ? 'default' : 'secondary'
                    }
                  >
                    {campaign.usage_paid_media_option ? 'Yes' : 'No'}
                  </Badge>
                </dd>
              </div>
            )}

          {campaign.exclusivity_category && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Exclusivity Category
              </dt>
              <dd className="text-sm">{campaign.exclusivity_category}</dd>
            </div>
          )}

          {campaign.exclusivity_days_before !== null &&
            campaign.exclusivity_days_before !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Exclusivity Days Before
                </dt>
                <dd className="text-sm">{campaign.exclusivity_days_before}</dd>
              </div>
            )}

          {campaign.exclusivity_days_after !== null &&
            campaign.exclusivity_days_after !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Exclusivity Days After
                </dt>
                <dd className="text-sm">{campaign.exclusivity_days_after}</dd>
              </div>
            )}

          {campaign.ownership_mode && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Ownership Mode
              </dt>
              <dd className="text-sm">
                <Badge variant="outline">{campaign.ownership_mode}</Badge>
              </dd>
            </div>
          )}

          {campaign.approval_rounds !== null &&
            campaign.approval_rounds !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Approval Rounds
                </dt>
                <dd className="text-sm">{campaign.approval_rounds}</dd>
              </div>
            )}

          {campaign.approval_sla_hours !== null &&
            campaign.approval_sla_hours !== undefined && (
              <div className="space-y-1">
                <dt className="text-muted-foreground text-sm font-medium">
                  Approval SLA
                </dt>
                <dd className="text-sm">{campaign.approval_sla_hours} hours</dd>
              </div>
            )}

          {campaign.assigned_roster_id && (
            <div className="space-y-1">
              <dt className="text-muted-foreground text-sm font-medium">
                Assigned Roster ID
              </dt>
              <dd className="text-sm">
                {formatValue(campaign.assigned_roster_id)}
              </dd>
            </div>
          )}

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Brand ID
            </dt>
            <dd className="text-sm">{campaign.brand_id}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Created At
            </dt>
            <dd className="text-sm">{formatDate(campaign.created_at)}</dd>
          </div>

          <div className="space-y-1">
            <dt className="text-muted-foreground text-sm font-medium">
              Updated At
            </dt>
            <dd className="text-sm">{formatDate(campaign.updated_at)}</dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  );
}
