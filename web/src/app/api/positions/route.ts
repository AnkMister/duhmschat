import { auth } from '@clerk/nextjs/server';
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// Validation schema for position
const positionSchema = z.object({
  symbol: z.string().min(1).max(10).transform(s => s.toUpperCase()),
  optionType: z.enum(['call', 'put']),
  strikePrice: z.number().positive(),
  expirationDate: z.string().refine(s => !isNaN(Date.parse(s)), 'Invalid date'),
  quantity: z.number().int().refine(n => n !== 0, 'Quantity cannot be zero'),
  premiumPaid: z.number().nonnegative(),
  purchaseDate: z.string().refine(s => !isNaN(Date.parse(s)), 'Invalid date').optional(),
});

// In production, this would connect to a database
// For now, we'll return mock data or proxy to Python backend

export async function GET(request: NextRequest) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    // In production: fetch from database filtered by userId
    // For demo: return empty array (positions stored client-side)
    return NextResponse.json({ positions: [], userId });
  } catch (error) {
    console.error('Error fetching positions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch positions' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const validated = positionSchema.parse(body);

    // In production: save to database with userId
    const position = {
      id: crypto.randomUUID(),
      userId,
      ...validated,
      purchaseDate: validated.purchaseDate || new Date().toISOString().split('T')[0],
      createdAt: new Date().toISOString(),
    };

    return NextResponse.json({ position }, { status: 201 });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Error creating position:', error);
    return NextResponse.json(
      { error: 'Failed to create position' },
      { status: 500 }
    );
  }
}
