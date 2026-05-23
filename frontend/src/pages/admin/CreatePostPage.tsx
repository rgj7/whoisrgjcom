import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { API_BASE } from "@/lib/api";
import { type PostFormData, PostForm } from "./PostForm";

export function CreatePostPage() {
  const navigate = useNavigate();

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
        body: JSON.stringify(data),
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

  return <PostForm mode="create" onSubmit={handleSubmit} />;
}

export default CreatePostPage;
