import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import { API_BASE } from "@/lib/api";
import { type PostFormData, PostForm } from "./PostForm";

export function CreatePostPage() {
  const navigate = useNavigate();

  const handleSubmit = async (data: PostFormData) => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
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

      toast.success("Post created successfully");
      navigate("/dashboard/posts");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to create post");
    }
  };

  return <PostForm mode="create" onSubmit={handleSubmit} />;
}

export default CreatePostPage;
