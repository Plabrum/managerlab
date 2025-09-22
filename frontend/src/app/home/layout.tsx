export default function HomeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="bg-background min-h-screen">
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  );
}
