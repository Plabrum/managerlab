'use client';
import { Button } from '@/components/ui/button';
import { Navbar } from '@/components/navbar';
import { Footer } from '@/components/footer';
import { FooterSection } from '@/components/footer-section';
import { FooterLink } from '@/components/footer-link';
import { NavigationItem } from '@/components/navigation-item';
import Link from 'next/link';
import { useUsersSignupAddUserToWaitlist } from '@/openapi/users/users';
import { createTypedForm } from '@/components/forms/base';
import { UserWaitlistFormSchema } from '@/openapi/litestarAPI.schemas';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const router = useRouter();

  const waitlist = useUsersSignupAddUserToWaitlist();

  const { Form, FormString, FormEmail, FormText } =
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
            <Link href="/auth">
              <Button
                variant="ghost"
                size="sm"
                className="text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                Sign In
              </Button>
            </Link>
            <Button size="sm" className="bg-white text-black hover:bg-gray-200">
              Get Started
            </Button>
          </div>
        }
      >
        <NavigationItem href="/#managers">For Managers</NavigationItem>
        <NavigationItem href="/#creators">For Creators</NavigationItem>
        <NavigationItem href="/#brands">For Brands</NavigationItem>
      </Navbar>

      <div className="min-h-screen bg-black text-white">
        <div className="container mx-auto px-4 py-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl">
            <div className="mb-12 text-center">
              <h1 className="mb-4 text-4xl font-bold text-white sm:text-5xl">
                Join the Waitlist
              </h1>
              <p className="text-xl text-zinc-400">
                Be among the first to experience Arive. Get early access and
                help shape the future of creator management.
              </p>
            </div>

            <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8">
              <Form
                onSubmit={async (values) => {
                  try {
                    await waitlist.mutateAsync({ data: values });
                    toast.success(
                      "You're on the waitlist! We will be in touch soon."
                    );
                    router.push('/');
                  } catch (error) {
                    toast.error('Something went wrong. Please try again.');
                    console.error(error);
                  }
                }}
                className="space-y-6"
              >
                <FormString name="name" label="Full Name" required autoFocus />
                <FormEmail name="email" label="Email Address" required />
                <FormString name="company" label="Company (Optional)" />
                <FormText
                  name="message"
                  label="Tell us more (Optional)"
                  rows={3}
                />
                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    disabled={waitlist.isPending}
                    className="flex-1 bg-white text-black hover:bg-zinc-200 disabled:opacity-50"
                  >
                    {waitlist.isPending ? 'Please wait...' : 'Join Waitlist'}
                  </Button>
                  <Link href="/" className="flex-1">
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full border-zinc-700 bg-transparent text-zinc-300 hover:bg-zinc-800 hover:text-white"
                    >
                      Cancel
                    </Button>
                  </Link>
                </div>
              </Form>
            </div>
          </div>
        </div>
      </div>

      <Footer>
        <FooterSection title="Product">
          <FooterLink href="/#managers">For Managers</FooterLink>
          <FooterLink href="/#creators">For Creators</FooterLink>
          <FooterLink href="/#brands">For Brands</FooterLink>
          <FooterLink href="/signup">Get Started</FooterLink>
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
