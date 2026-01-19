import { NextResponse } from 'next/server'
import { readFileSync } from 'fs'
import { join } from 'path'

/**
 * Health Check Endpoint
 *
 * Returns service health status and BUILD_ID for verification
 *
 * P0 Fix: Added BUILD_ID to verify correct build is running
 * (prevents 500 errors from stale chunk serving)
 */
export async function GET() {
  try {
    // Read BUILD_ID from .next/BUILD_ID
    const buildIdPath = join(process.cwd(), '.next', 'BUILD_ID')
    const buildId = readFileSync(buildIdPath, 'utf-8').trim()

    return NextResponse.json({
      status: 'healthy',
      buildId,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    // If BUILD_ID not found, service is unhealthy
    return NextResponse.json(
      {
        status: 'unhealthy',
        error: 'BUILD_ID not found',
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    )
  }
}
