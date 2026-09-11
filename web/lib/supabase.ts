import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  global: {
    fetch: (url, options = {}) => fetch(url, { ...options, cache: 'no-store' }),
  },
})

// 型定義
export interface Comedian {
  id: number
  slug: string
  name: string
  name_kana?: string
  unit_type: 'combi' | 'trio' | 'pin' | 'unit' | 'other'
  agency?: string
  formed_year?: number
  is_active: boolean
}

export interface NetaWork {
  id: number
  comedian_id: number
  title?: string
  format: 'manzai' | 'conte' | 'pin' | 'other'
  setting_note?: string
}

export interface Performance {
  id: number
  neta_work_id?: number
  video_id: string
  start_sec: number
  end_sec?: number
  review_status: 'pending' | 'approved' | 'rejected'
  source: 'llm' | 'manual'
}

export interface YTVideo {
  video_id: string
  channel_id: string
  title?: string
  description?: string
  published_at?: string
  duration_sec?: number
  thumbnail_url?: string
  embeddable?: boolean
  privacy_status?: string
  view_count?: number
}

export interface Tag {
  id: number
  slug: string
  name: string
  category: 'place' | 'relation' | 'job' | 'theme' | 'style'
}

export interface Contest {
  id: number
  slug: string
  name: string
}

// クエリ関数
export async function searchNetas(query: string, limit: number = 20) {
  const { data, error } = await supabase
    .rpc('search_netas', {
      search_query: query,
      result_limit: limit,
    })

  if (error) throw error
  return data
}

export async function getAllComedians() {
  const { data, error } = await supabase
    .from('comedians')
    .select('*')
    .eq('is_active', true)
    .order('name')

  if (error) throw error
  return data as Comedian[]
}

export async function getComedianBySlug(slug: string) {
  const { data, error } = await supabase
    .from('comedians')
    .select('*')
    .eq('slug', slug)
    .single()

  if (error) throw error
  return data as Comedian
}

export async function getComedianNetas(comedianId: number) {
  const { data, error } = await supabase
    .from('neta_works')
    .select(`
      id,
      title,
      format,
      setting_note,
      performances (
        id,
        video_id,
        start_sec,
        end_sec,
        review_status,
        source,
        yt_videos (thumbnail_url, duration_sec)
      ),
      neta_work_tags (
        tag_id,
        status,
        confidence,
        tags (slug, name)
      )
    `)
    .eq('comedian_id', comedianId)
    .eq('performances.review_status', 'approved')

  if (error) throw error
  return data
}

export async function getNetaById(id: number) {
  const { data, error } = await supabase
    .from('neta_works')
    .select(`
      id,
      title,
      format,
      setting_note,
      comedians (id, slug, name),
      performances (
        video_id,
        start_sec,
        end_sec,
        yt_videos (title, description, duration_sec, thumbnail_url)
      ),
      neta_work_tags (
        status,
        confidence,
        tags (slug, name, category)
      )
    `)
    .eq('id', id)
    .single()

  if (error) throw error
  return data as any
}

export async function getTagNetas(slug: string, limit: number = 50) {
  const { data: tag, error: tagError } = await supabase
    .from('tags')
    .select('id')
    .eq('slug', slug)
    .single()

  if (tagError) throw tagError

  const { data, error } = await supabase
    .from('neta_work_tags')
    .select(`
      neta_work_id,
      status,
      confidence,
      neta_works (
        id,
        title,
        format,
        comedians (slug, name),
        performances (video_id, yt_videos (thumbnail_url, duration_sec))
      )
    `)
    .eq('tag_id', tag.id)
    .eq('status', 'approved')
    .order('confidence', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}

export async function getContestNetas(slug: string, year: number) {
  const { data: contest, error: contestError } = await supabase
    .from('contests')
    .select('id')
    .eq('slug', slug)
    .single()

  if (contestError) throw contestError

  const { data: edition, error: editionError } = await supabase
    .from('contest_editions')
    .select('id')
    .eq('contest_id', contest.id)
    .eq('year', year)
    .single()

  if (editionError) throw editionError

  const { data, error } = await supabase
    .from('contest_entries')
    .select(`
      id,
      order_no,
      rank,
      score,
      round,
      comedians (id, slug, name),
      performances (
        id,
        neta_work_id,
        video_id,
        start_sec,
        end_sec,
        yt_videos (thumbnail_url, duration_sec)
      )
    `)
    .eq('edition_id', edition.id)
    .order('order_no', { ascending: true })

  if (error) throw error
  return data
}

export async function getAllTags() {
  const { data, error } = await supabase
    .from('tags')
    .select('*')
    .order('category')

  if (error) throw error
  return data as Tag[]
}

export async function getContestBySlug(slug: string) {
  const { data, error } = await supabase
    .from('contests')
    .select('*')
    .eq('slug', slug)
    .single()

  if (error) throw error
  return data as Contest
}

export async function getContestEditions(contestId: number) {
  const { data, error } = await supabase
    .from('contest_editions')
    .select('id, year')
    .eq('contest_id', contestId)
    .order('year', { ascending: false })

  if (error) throw error
  return data as { id: number; year: number }[]
}

export async function getAllContests() {
  const { data, error } = await supabase
    .from('contests')
    .select('*')

  if (error) throw error
  return data as Contest[]
}

export async function createTakedownRequest(targetUrl: string, requester: string, reason: string) {
  const { error } = await supabase
    .from('takedown_requests')
    .insert({ target_url: targetUrl, requester, reason })

  if (error) throw error
}
