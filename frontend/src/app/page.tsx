'use client';

import { Button } from '@/components/ui/button';
import { FeatureSection } from '@/components/feature-section';
import { FeatureCard } from '@/components/feature-card';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { FooterSection } from '@/components/footer-section';
import { FooterLink } from '@/components/footer-link';
import { NavigationItem } from '@/components/navigation-item';
import { useState } from 'react';
import {
  Users,
  Zap,
  Shield,
  Calendar,
  CreditCard,
  Upload,
  BarChart3,
  Clock,
  DollarSign,
  CheckCircle,
} from 'lucide-react';
import { UserWaitlistFormSchema } from '@/openapi/litestarAPI.schemas';
import { useUsersSignupAddUserToWaitlist } from '@/openapi/users/users';
import { createTypedForm } from '@/components/forms/base';
import { toast } from 'sonner';
import Link from 'next/link';

export default function LandingPage() {
  const [isWaitlistModalOpen, setIsWaitlistModalOpen] = useState(false);

  const waitlist = useUsersSignupAddUserToWaitlist();

  const { FormModal, FormString, FormEmail, FormText } =
    createTypedForm<UserWaitlistFormSchema>();

  return (
    <>
      <Navbar
        brand={
          <Link href="/" className="text-2xl font-bold text-white">
            Arive
          </Link>
        }
        actions={
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              className="text-gray-300 hover:bg-gray-800 hover:text-white"
            >
              Sign In
            </Button>
            <Button
              onClick={() => setIsWaitlistModalOpen(true)}
              size="sm"
              className="bg-white text-black hover:bg-gray-200"
            >
              Get Started
            </Button>
          </div>
        }
      >
        <NavigationItem href="#managers">For Managers</NavigationItem>
        <NavigationItem href="#creators">For Creators</NavigationItem>
        <NavigationItem href="#brands">For Brands</NavigationItem>
      </Navbar>

      <div className="min-h-screen bg-black text-white">
        {/* Hero Section */}
        <section className="relative flex min-h-[80vh] items-center justify-center">
          <div className="container mx-auto px-4 text-center sm:px-6 lg:px-8">
            <div className="mx-auto max-w-4xl space-y-8">
              <h1 className="text-5xl font-bold leading-tight text-white sm:text-6xl lg:text-7xl">
                Next Generation Talent,{' '}
                <span className="block">Organized.</span>
              </h1>
              <div className="flex flex-col items-center justify-center gap-4 pt-8 sm:flex-row">
                <Button
                  size="lg"
                  className="bg-white px-8 py-6 text-lg text-black hover:bg-gray-200"
                  onClick={() => setIsWaitlistModalOpen(true)}
                >
                  Get Started
                </Button>
                <Button
                  variant="outline"
                  size="lg"
                  className="border-gray-600 bg-transparent px-8 py-6 text-lg text-white hover:bg-gray-800"
                  onClick={() => setIsWaitlistModalOpen(true)}
                >
                  Get Started
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Sections */}
        <FeatureSection id="managers" title="For Managers" gridCols="2">
          <FeatureCard
            icon={<Zap className="h-8 w-8" />}
            title="Accounts Receivable Management"
            description="Auto generated invoices with templated reminders for agencies and brands."
          />
          <FeatureCard
            icon={<Users className="h-8 w-8" />}
            title="Accounts Payable Management"
            description="Seamlessly generate payments to Creators on your Roster with automatic notifications for your clients."
          />
          <FeatureCard
            icon={<Shield className="h-8 w-8" />}
            title="Roster Management"
            description="View and share your roster with agencies to market based on specific filters."
          />
          <FeatureCard
            icon={<BarChart3 className="h-8 w-8" />}
            title="Performance Dashboards"
            description="Review revenue metrics and other key performance indicators."
          />
        </FeatureSection>

        <FeatureSection id="creators" title="For Creators" gridCols="2">
          <FeatureCard
            icon={<Calendar className="h-8 w-8" />}
            title="Campaign Tracking"
            description="Due date reminders and total earnings information."
          />
          <FeatureCard
            icon={<CreditCard className="h-8 w-8" />}
            title="Payment Status"
            description="Track your outstanding invoices so you know when you're getting paid."
          />
          <FeatureCard
            icon={<Clock className="h-8 w-8" />}
            title="Scheduled Uploads"
            description="Schedule your content uploads in advance and automate your posting workflow."
          />
          <FeatureCard
            icon={<Upload className="h-8 w-8" />}
            title="Content Uploads and Permissions"
            description="Easily share video and audio content without sacrificing quality or having to create a separate upload link. Toggle permissions for Manager and Agency review."
          />
        </FeatureSection>

        <FeatureSection id="brands" title="For Brands" gridCols="3">
          <FeatureCard
            icon={<BarChart3 className="h-8 w-8" />}
            title="Campaign Analytics"
            description="Track performance metrics and ROI across all your influencer campaigns."
          />
          <FeatureCard
            icon={<DollarSign className="h-8 w-8" />}
            title="Bill Pay Portal"
            description="Streamlined payment processing for all your creator partnerships and campaigns."
          />
          <FeatureCard
            icon={<CheckCircle className="h-8 w-8" />}
            title="Deliverable Approval"
            description="Review and approve content deliverables with integrated feedback and revision tools."
          />
        </FeatureSection>
      </div>

      <Footer>
        <FooterSection title="Product">
          <FooterLink href="#managers">For Managers</FooterLink>
          <FooterLink href="#creators">For Creators</FooterLink>
          <FooterLink href="#brands">For Brands</FooterLink>
          <button
            onClick={() => setIsWaitlistModalOpen(true)}
            className="text-left text-gray-400 transition-colors hover:text-white"
          >
            Get Started
          </button>
        </FooterSection>
        {/* <FooterSection title="Company"> */}
        {/*   <FooterLink href="/about">About</FooterLink> */}
        {/*   <FooterLink href="/careers">Careers</FooterLink> */}
        {/*   <FooterLink href="/blog">Blog</FooterLink> */}
        {/* </FooterSection> */}
        {/* <FooterSection title="Support"> */}
        {/*   <FooterLink href="/help">Help Center</FooterLink> */}
        {/*   <FooterLink href="/docs">Documentation</FooterLink> */}
        {/*   <FooterLink href="/status">Status</FooterLink> */}
        {/* </FooterSection> */}
        {/* <FooterSection title="Legal"> */}
        {/*   <FooterLink href="/privacy">Privacy Policy</FooterLink> */}
        {/*   <FooterLink href="/terms">Terms of Service</FooterLink> */}
        {/* </FooterSection> */}
      </Footer>

      <FormModal
        isOpen={isWaitlistModalOpen}
        onClose={() => setIsWaitlistModalOpen(false)}
        title="Join the Waitlist"
        subTitle="Be among the first to experience Arive."
        onSubmit={async (values) => {
          await waitlist.mutateAsync({ data: values });
          setIsWaitlistModalOpen(false);
          toast("You're on the waitlist! We will be in touch soon.");
        }}
        isSubmitting={waitlist.isPending}
        submitText="Join Waitlist"
      >
        <FormString name="name" label="Full Name" required autoFocus />
        <FormEmail name="email" label="Email Address" required />
        <FormString name="company" label="Company (Optional)" />
        <FormText name="message" label="Tell us more (Optional)" rows={3} />
      </FormModal>
    </>
  );
}
