import type React from 'react';

interface FeatureSectionProps {
  id: string;
  title: string;
  children: React.ReactNode;
  gridCols?: '2' | '3';
}

export function FeatureSection({
  id,
  title,
  children,
  gridCols = '2',
}: FeatureSectionProps) {
  const gridClass = gridCols === '3' ? 'md:grid-cols-3' : 'md:grid-cols-2';

  return (
    <section id={id} className="bg-black py-24">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <h2 className="mb-8 text-3xl font-black text-white sm:text-4xl">
            {title}
          </h2>
        </div>

        <div className={`grid ${gridClass} mx-auto max-w-4xl gap-8`}>
          {children}
        </div>
      </div>
    </section>
  );
}
