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
