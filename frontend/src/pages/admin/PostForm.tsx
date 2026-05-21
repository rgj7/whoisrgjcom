import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

export interface PostFormData {
  title: string;
  slug: string;
  content: string;
  excerpt: string | null;
  published: boolean;
}

export interface PostFormProps {
  mode: "create" | "edit";
  initialData?: PostFormData;
  isSubmitting?: boolean;
  onSubmit: (data: PostFormData) => Promise<void> | void;
}

export function PostForm({ mode, initialData, isSubmitting = false, onSubmit }: PostFormProps) {
  const [title, setTitle] = useState(initialData?.title ?? "");
  const [slug, setSlug] = useState(initialData?.slug ?? "");
  const [content, setContent] = useState(initialData?.content ?? "");
  const [excerpt, setExcerpt] = useState(initialData?.excerpt ?? "");
  const [published, setPublished] = useState(initialData?.published ?? true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !slug.trim() || !content.trim()) return;

    await onSubmit({
      title: title.trim(),
      slug: slug.trim(),
      content,
      excerpt: excerpt.trim() || null,
      published,
    });
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{mode === "create" ? "New Post" : "Edit Post"}</h1>
        <Button variant="outline" onClick={() => window.history.back()}>
          Back to Posts
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <Label htmlFor="title">Title</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Post title"
            required
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="slug">Slug</Label>
          <Input
            id="slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="post-slug"
            required
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="content">Content</Label>
          <Textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Post content"
            rows={12}
            required
          />
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="excerpt">Excerpt (optional)</Label>
          <Input
            id="excerpt"
            value={excerpt}
            onChange={(e) => setExcerpt(e.target.value)}
            placeholder="Short excerpt"
            maxLength={500}
          />
        </div>

        <div className="flex items-center gap-2">
          <Label>Status</Label>
          <Badge
            variant={published ? "default" : "secondary"}
            className="cursor-pointer"
            onClick={() => setPublished((p) => !p)}
          >
            {published ? "Published" : "Unpublished"}
          </Badge>
        </div>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting
            ? mode === "create"
              ? "Creating…"
              : "Saving…"
            : mode === "create"
              ? "Create Post"
              : "Save Changes"}
        </Button>
      </form>
    </div>
  );
}
