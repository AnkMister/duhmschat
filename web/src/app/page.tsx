import Link from 'next/link';
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Target,
  Bell,
  LineChart,
  Shield,
  Smartphone,
  Zap,
  ChevronRight,
} from 'lucide-react';

export default async function HomePage() {
  const { userId } = await auth();

  if (userId) {
    redirect('/dashboard');
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Target className="h-6 w-6 text-primary" />
            <span className="font-bold text-lg">Options Monitor</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" asChild>
              <Link href="/sign-in">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/sign-up">Get Started</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm text-primary mb-6">
          <Zap className="h-4 w-4" />
          Real-time ITM Alerts
        </div>

        <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
          Never Miss an
          <span className="text-primary"> In-The-Money </span>
          Option Again
        </h1>

        <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
          Track your options portfolio, get instant alerts when positions go ITM,
          and receive AI-powered insights to optimize your trades.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button size="lg" asChild>
            <Link href="/sign-up">
              Start Free <ChevronRight className="h-4 w-4 ml-2" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <Link href="/sign-in">Sign In</Link>
          </Button>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything You Need to Monitor Your Options
        </h2>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-itm-muted flex items-center justify-center mb-4">
                <Target className="h-6 w-6 text-itm" />
              </div>
              <h3 className="text-lg font-semibold mb-2">ITM Detection</h3>
              <p className="text-muted-foreground">
                Automatically detect when your options go In-The-Money and get instant notifications.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Bell className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Smart Alerts</h3>
              <p className="text-muted-foreground">
                Customizable rules for expiration warnings, profit targets, and stop losses.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <LineChart className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Portfolio Analytics</h3>
              <p className="text-muted-foreground">
                See your entire options portfolio at a glance with P/L tracking and insights.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Secure Connection</h3>
              <p className="text-muted-foreground">
                Connect your brokerage securely via SnapTrade. We never store your credentials.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Smartphone className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Mobile First</h3>
              <p className="text-muted-foreground">
                Install as a PWA on your phone for native-like experience with push notifications.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">AI Insights</h3>
              <p className="text-muted-foreground">
                Get AI-powered recommendations on when to take profits or cut losses.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-20">
        <Card className="bg-primary text-primary-foreground">
          <CardContent className="py-12 text-center">
            <h2 className="text-3xl font-bold mb-4">
              Start Monitoring Your Options Today
            </h2>
            <p className="text-primary-foreground/80 mb-8 max-w-xl mx-auto">
              Join traders who use Options Monitor to stay on top of their positions
              and never miss an opportunity.
            </p>
            <Button size="lg" variant="secondary" asChild>
              <Link href="/sign-up">
                Get Started Free <ChevronRight className="h-4 w-4 ml-2" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} Options Monitor. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
