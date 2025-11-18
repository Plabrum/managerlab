import { Heading, Section, Text } from '@react-email/components';
import * as React from 'react';
import { BaseLayout, Button } from './components';

interface CampaignCreatedFromAttachmentProps {
  campaign_name: string;
  campaign_link: string;
  sender_email: string;
  extraction_notes?: string;
}

export default function CampaignCreatedFromAttachment({
  campaign_name = 'Summer Beauty Campaign 2025',
  campaign_link = 'https://tryarive.com/campaigns/abc123',
  sender_email = 'partner@brand.com',
  extraction_notes = null,
}: CampaignCreatedFromAttachmentProps) {
  return (
    <BaseLayout preview={`Your campaign "${campaign_name}" has been created`}>
      <Section className="mb-6">
        <Heading className="mx-0 my-[30px] p-0 text-center font-normal text-[28px] text-black">
          Your Campaign Has Been Created
        </Heading>
      </Section>

      <Text className="text-muted-foreground text-base leading-relaxed mb-6 font-normal">
        Thanks for sending your contract! We've processed the document and created a new campaign:
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

      {/* Extraction notes if available */}
      {extraction_notes && (
        <Section className="mt-8 mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <Text className="text-foreground text-sm leading-relaxed m-0">
            <strong className="text-blue-700 font-semibold">Note from our AI:</strong>
            <br />
            {extraction_notes}
          </Text>
        </Section>
      )}

      {/* Next steps */}
      <Section className="mt-8 mb-6 p-4 bg-green-50 rounded-lg border border-success">
        <Text className="text-foreground text-sm leading-relaxed m-0">
          <strong className="text-success font-semibold">Next Steps:</strong>
          <br />
          1. Review the extracted campaign details for accuracy
          <br />
          2. Make any necessary adjustments
          <br />
          3. Invite collaborators or start planning deliverables
        </Text>
      </Section>

      {/* Footer note */}
      <Section className="mt-6 p-4 bg-neutral-50 rounded-lg border border-neutral-100">
        <Text className="text-muted-foreground text-sm leading-relaxed m-0">
          <strong className="text-foreground font-semibold">Questions?</strong>
          <br />
          If anything looks incorrect or you need help, just reply to this email
          and we'll be happy to assist.
        </Text>
      </Section>
    </BaseLayout>
  );
}
