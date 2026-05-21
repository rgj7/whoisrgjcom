import useSWR from "swr";

const API_BASE =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://localhost:8000";

export interface Post {
  id: string;
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  created_at: string;
  updated_at: string;
}

const POST_TIMEOUT_MS = 5_000;

async function fetcher< T >(url: string): Promise<T> {
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

export function usePosts() {
  return useSWR<Post[]>(`${API_BASE}/posts/`, fetcher, {
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

export async function getMe(token: string): Promise<CurrentUser> {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new Error(`Token validation failed: ${res.status}`);
  }
  return res.json();
}
