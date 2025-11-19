import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout, Button } from './components';

interface CampaignCreatedFromAttachmentProps {
  user_name: string;
  campaign_name: string;
  campaign_link: string;
  sender_email: string;
}

export default function CampaignCreatedFromAttachment({
  user_name = 'Alex',
  campaign_name = 'Summer Beauty Campaign 2025',
  campaign_link = 'https://tryarive.com/campaigns/abc123',
  sender_email = 'partner@brand.com',
}: CampaignCreatedFromAttachmentProps) {
  return (
    <BaseLayout preview={`Your campaign "${campaign_name}" has been created`}>
      {/* Personal Greeting */}
      <Section className="mb-8">
        <Text className="text-foreground text-base leading-relaxed mb-0 font-normal">
          Hi {user_name},
        </Text>
      </Section>

      <Text className="text-muted-foreground text-base leading-relaxed mb-6 font-normal">
        Great news! We've processed the contract you sent from <strong className="text-foreground">{sender_email}</strong> and created a new campaign for you:
      </Text>

      <Section className="my-8 p-6 bg-neutral-50 border border-border rounded-lg">
        <Text className="text-foreground text-lg font-semibold m-0 mb-2">
          {campaign_name}
        </Text>
        <Text className="text-muted-foreground text-sm m-0">
          We've extracted the key details from your contract and set up the campaign for you.
        </Text>
      </Section>

      <Section className="my-8 text-center">
        <Button href={campaign_link}>View Campaign</Button>
      </Section>

      {/* Alternative link section */}
      <Section className="mt-12 mb-8">
        <Text className="text-[13px] text-neutral-400 mb-2 font-medium uppercase tracking-wider m-0">
          Or copy this link:
        </Text>
        <div className="bg-neutral-50 border border-border rounded-lg p-4">
          <Text className="text-muted-foreground text-[13px] break-all m-0 leading-normal font-mono">
            {campaign_link}
          </Text>
        </div>
      </Section>

      {/* Next steps */}
      <Section className="mt-8 mb-6">
        <Text className="text-foreground text-base font-semibold mb-3 mt-0">
          What's next?
        </Text>
        <Text className="text-muted-foreground text-sm leading-relaxed m-0">
          • Review the campaign details to make sure everything looks right
          <br />
          • Add any missing information or make adjustments
          <br />
          • Invite team members or start planning your deliverables
        </Text>
      </Section>
    </BaseLayout>
  );
}
