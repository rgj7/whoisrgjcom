import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";

import { API_BASE, useAdminPostById } from "@/lib/api";
import { type PostFormData, PostForm } from "./PostForm";

export function EditPostPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { data: post, isLoading, error } = useAdminPostById(id ?? "");

  useEffect(() => {
    if (error) {
      toast.error("Failed to load post");
      navigate("/dashboard/posts");
    }
  }, [error, navigate]);

  const handleSubmit = async (data: PostFormData) => {
    if (!id) return;

    setIsSubmitting(true);
    const token = localStorage.getItem("token");
    if (!token) return;

    try {
      const res = await fetch(`${API_BASE}/admin/posts/${id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const body = await res.text();
        throw new Error(`Failed to update post: ${res.status} ${body}`);
      }

      toast.success("Post updated successfully");
      navigate("/dashboard/posts");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to update post");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
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
      }}
      isSubmitting={isSubmitting}
      onSubmit={handleSubmit}
    />
  );
}

export default EditPostPage;
