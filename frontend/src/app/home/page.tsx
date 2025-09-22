import { CurrentUserTest } from '@/components/current-user-test';

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section>
        <CurrentUserTest />
      </section>
    </div>
  );
}
