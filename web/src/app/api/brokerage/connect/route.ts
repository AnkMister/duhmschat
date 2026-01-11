import { auth } from '@clerk/nextjs/server';
import { NextRequest, NextResponse } from 'next/server';
import { getSnapTradeClient } from '@/lib/snaptrade';

/**
 * POST /api/brokerage/connect
 *
 * Initiates brokerage connection via SnapTrade.
 * Returns a login link for the user to connect their brokerage.
 */
export async function POST(request: NextRequest) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { broker } = body; // Optional: specific broker to connect

    const client = getSnapTradeClient();

    // Register user with SnapTrade (idempotent - returns existing if already registered)
    let userSecret: string;

    try {
      const snapUser = await client.registerUser(userId);
      userSecret = snapUser.userSecret;

      // Store userSecret securely (in production: encrypt and save to database)
      // For now, we'll pass it back to the client (not ideal, but for demo)
    } catch (error: any) {
      // User might already exist
      if (error.message.includes('already exists')) {
        // In production: retrieve stored userSecret from database
        return NextResponse.json(
          { error: 'User already registered. Please use existing connection.' },
          { status: 409 }
        );
      }
      throw error;
    }

    // Get login link for OAuth flow
    const { loginLink } = await client.getLoginLink(userId, userSecret, broker);

    return NextResponse.json({
      loginLink,
      // In production, don't send userSecret to client
      // Instead, store it encrypted in database
    });
  } catch (error) {
    console.error('Brokerage connection error:', error);

    if (error instanceof Error && error.message.includes('not configured')) {
      return NextResponse.json(
        { error: 'Brokerage integration not configured' },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: 'Failed to initiate brokerage connection' },
      { status: 500 }
    );
  }
}

/**
 * GET /api/brokerage/connect
 *
 * List user's connected brokerages
 */
export async function GET(request: NextRequest) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // In production: retrieve userSecret from database
    const userSecret = request.headers.get('X-User-Secret');

    if (!userSecret) {
      return NextResponse.json({ connections: [] });
    }

    const client = getSnapTradeClient();
    const authorizations = await client.listAuthorizations(userId, userSecret);

    return NextResponse.json({
      connections: authorizations.map((auth) => ({
        id: auth.id,
        brokerage: auth.brokerage.name,
        brokerageSlug: auth.brokerage.slug,
        accounts: auth.accounts.map((acc) => ({
          id: acc.id,
          number: acc.number,
          name: acc.name,
        })),
      })),
    });
  } catch (error) {
    console.error('Error fetching connections:', error);
    return NextResponse.json(
      { error: 'Failed to fetch brokerage connections' },
      { status: 500 }
    );
  }
}
