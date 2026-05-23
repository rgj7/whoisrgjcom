import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";

import { API_BASE, type Tag, useAdminPostById, searchTags } from "@/lib/api";
import { type PostFormData, PostForm } from "./PostForm";

export function EditPostPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [existingTags, setExistingTags] = useState<Tag[]>([]);
  const [tagsLoaded, setTagsLoaded] = useState(false);
  const token = localStorage.getItem("token");

  const { data: post, isLoading, error } = useAdminPostById(id ?? "");

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

  useEffect(() => {
    if (error) {
      toast.error("Failed to load post");
      navigate("/dashboard/posts");
    }
  }, [error, navigate]);

  const savePost = async (data: PostFormData): Promise<{ success: boolean; error?: string }> => {
    if (!id) {
      return { success: false, error: "Post ID is missing" };
    }

    setIsSubmitting(true);
    const token = localStorage.getItem("token");
    if (!token) {
      return { success: false, error: "Not authenticated" };
    }

    try {
      const res = await fetch(`${API_BASE}/admin/posts/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ ...data, tags: data.tags }),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Failed to update post: ${res.status} ${body}`);
      }

      return { success: true };
    } catch (err) {
      return { success: false, error: err instanceof Error ? err.message : "Failed to update post" };
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (data: PostFormData) => {
    const result = await savePost(data);
    if (result.success) {
      toast.success("Post updated successfully");
    } else {
      toast.error(result.error);
    }
  };

  if (isLoading || !tagsLoaded) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  if (!post) return null;

  return (
    <PostForm
      mode="edit"
      initialData={{
        title: post.title,
        slug: post.slug,
        content: post.content,
        excerpt: post.excerpt ?? "",
        published: post.published,
        tags: post.tags ?? [],
      }}
      existingTags={existingTags.map((t) => ({ value: t.name, label: t.name }))}
      isSubmitting={isSubmitting}
      onSubmit={handleSubmit}
      authToken={token ?? undefined}
    />
  );
}

export default EditPostPage;
