import useSWR from "swr";
import type { JSONContent } from "@tiptap/react";

export const API_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";

export interface Tag {
  id: string;
  name: string;
}

export interface Post {
  id: string;
  title: string;
  slug: string;
  content: JSONContent;
  excerpt: string | null;
  published: boolean;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export interface PaginatedPosts {
  items: Post[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

const POST_TIMEOUT_MS = 5_000;

async function fetcher<T>(url: string): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), POST_TIMEOUT_MS);

  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`Failed to fetch ${url}: ${res.status} ${body}`);
    }
    return res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

export function usePosts(page: number = 1, limit: number = 10) {
  const url = `${API_BASE}/posts/?page=${page}&limit=${limit}`;
  return useSWR<PaginatedPosts>(url, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 0,
  });
}

export function useAdminPosts(page: number = 1, limit: number = 10) {
  const url = `${API_BASE}/admin/posts/?page=${page}&limit=${limit}`;
  return useSWR<PaginatedPosts>(url, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 0,
  });
}

export function usePostBySlug(slug: string) {
  return useSWR<Post>(slug ? `${API_BASE}/posts/slug/${slug}` : null, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 0,
  });
}

export function usePostById(id: string) {
  return useSWR<Post>(id ? `${API_BASE}/posts/${id}` : null, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 0,
  });
}

export function useAdminPostById(id: string) {
  return useSWR<Post>(id ? `${API_BASE}/admin/posts/${id}` : null, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 0,
  });
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface CurrentUser {
  id: string;
  username: string;
  email: string;
  is_superuser: boolean;
  created_at: string;
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Login failed: ${res.status} ${body}`);
  }
  return res.json();
}

export async function searchTags(token: string, query: string): Promise<Tag[]> {
  const res = await fetch(`${API_BASE}/admin/tags/?search=${encodeURIComponent(query)}`,
    {
      headers: { Authorization: `Bearer ${token}` },
    },
  );
  if (!res.ok) {
    throw new Error(`Failed to search tags: ${res.status}`);
  }
  return res.json();
}

export async function getMe(token: string): Promise<CurrentUser> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new Error(`Token validation failed: ${res.status}`);
  }
  return res.json();
}

export async function deleteAdminPost(token: string, id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/admin/posts/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to delete post: ${res.status} ${body}`);
  }
}

export async function updateAdminPost(
  token: string,
  id: string,
  data: Partial<Post>,
): Promise<Post> {
  const res = await fetch(`${API_BASE}/admin/posts/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Failed to update post: ${res.status} ${body}`);
  }
  return res.json();
}
