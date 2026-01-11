/**
 * API 调用工具
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Story {
  id: number;
  hn_id: number;
  title: string;
  url: string | null;
  author: string;
  score: number;
  comments_count: number;
  posted_at: string;
  is_ai_related: boolean;
  hn_url: string;
  created_at: string;
  updated_at: string;
}

export interface StoriesResponse {
  items: Story[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface StatsResponse {
  total: number;
  ai_count: number;
  avg_score: number;
  top_score: number;
}

/**
 * 获取故事列表
 */
export async function fetchStories(params: {
  page?: number;
  size?: number;
  ai_only?: boolean;
  min_score?: number;
}): Promise<StoriesResponse> {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.append('page', params.page.toString());
  if (params.size) queryParams.append('size', params.size.toString());
  if (params.ai_only !== undefined) queryParams.append('ai_only', params.ai_only.toString());
  if (params.min_score) queryParams.append('min_score', params.min_score.toString());

  const response = await fetch(`${API_BASE_URL}/api/stories?${queryParams}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch stories: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 获取单个故事
 */
export async function fetchStory(id: number): Promise<Story> {
  const response = await fetch(`${API_BASE_URL}/api/stories/${id}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch story: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 获取统计信息
 */
export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/stats`);

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * 触发爬取
 */
export async function triggerCrawl(): Promise<{ message: string; status: string }> {
  const response = await fetch(`${API_BASE_URL}/api/crawl`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Failed to trigger crawl: ${response.statusText}`);
  }

  return response.json();
}
