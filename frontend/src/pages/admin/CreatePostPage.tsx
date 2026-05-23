import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { API_BASE, type Tag, searchTags } from "@/lib/api";
import { type PostFormData, PostForm } from "./PostForm";

export function CreatePostPage() {
  const navigate = useNavigate();
  const [existingTags, setExistingTags] = useState<Tag[]>([]);
  const [tagsLoaded, setTagsLoaded] = useState(false);
  const token = localStorage.getItem("token");

  useEffect(() => {
    if (!token) return;
    const loadTags = async () => {
      try {
        const tags = await searchTags(token, "");
        setExistingTags(tags);
      } catch {
        // Ignore tag load errors
      } finally {
        setTagsLoaded(true);
      }
    };
    loadTags();
  }, [token]);

  const createPost = async (data: PostFormData): Promise<{ success: boolean; error?: string }> => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return { success: false, error: "Not authenticated" };
    }

    try {
      const res = await fetch(`${API_BASE}/admin/posts/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ ...data, tags: data.tags }),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Failed to create post: ${res.status} ${body}`);
      }

      return { success: true };
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : "Failed to create post" };
    }
  };

  const handleSubmit = async (data: PostFormData) => {
    const result = await createPost(data);
    if (result.success) {
      toast.success("Post created successfully");
      navigate("/dashboard/posts");
    } else {
      toast.error(result.error);
    }
  };

  if (!tagsLoaded) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  return (
    <PostForm
      mode="create"
      initialData={{
        title: "",
        slug: "",
        content: "",
        excerpt: "",
        published: true,
        tags: [],
      }}
      existingTags={existingTags.map((t) => ({ value: t.name, label: t.name }))}
      isSubmitting={false}
      onSubmit={handleSubmit}
      authToken={token ?? undefined}
    />
  );
}

export default CreatePostPage;
