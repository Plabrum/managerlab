import { Button } from '@/components/ui/button';
import { FeatureSection } from '@/components/feature-section';
import { FeatureCard } from '@/components/feature-card';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { FooterSection } from '@/components/footer-section';
import { FooterLink } from '@/components/footer-link';
import { NavigationItem } from '@/components/navigation-item';
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
import Link from 'next/link';

export function LandingPage() {
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
            <Link href="/auth">
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                Sign In
              </Button>
            </Link>
            <Link href="/auth?sign-up">
              <Button
                size="sm"
                className="bg-white text-black hover:bg-gray-200"
              >
                Get Started
              </Button>
            </Link>
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
                <Link href="/auth">
                  <Button
                    variant="outline"
                    size="lg"
                    className="border-gray-600 bg-transparent px-8 py-6 text-lg text-white hover:bg-gray-800"
                  >
                    Sign In
                  </Button>
                </Link>
                <Link href="/auth?sign-up">
                  <Button
                    size="lg"
                    className="bg-white px-8 py-6 text-lg text-black hover:bg-gray-200"
                  >
                    Get Started
                  </Button>
                </Link>
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
          <FooterLink href="/auth?sign-up">Get Started</FooterLink>
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
    </>
  );
}
