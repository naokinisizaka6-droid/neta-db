import { NextRequest, NextResponse } from 'next/server'
import { createTakedownRequest } from '@/lib/supabase'

export async function POST(req: NextRequest) {
  const form = await req.formData()
  const targetUrl = String(form.get('target_url') || '').trim()
  const requester = String(form.get('requester') || '').trim()
  const reason = String(form.get('reason') || '').trim()

  if (!targetUrl) {
    return NextResponse.redirect(new URL('/takedown?error=1', req.url))
  }

  try {
    await createTakedownRequest(targetUrl, requester, reason)
  } catch (e) {
    return NextResponse.redirect(new URL('/takedown?error=1', req.url))
  }

  return NextResponse.redirect(new URL('/takedown?sent=1', req.url))
}
