import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { MobileNav } from '@/components/layout/mobile-nav';

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { userId } = await auth();

  if (!userId) {
    redirect('/sign-in');
  }

  return (
    <div className="min-h-screen pb-20">
      {children}
      <MobileNav />
    </div>
  );
}
