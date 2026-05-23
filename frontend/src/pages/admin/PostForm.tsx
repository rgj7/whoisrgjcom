import { useState } from "react";
import type { SubmitEvent } from "react";
import type { JSONContent } from "@tiptap/react";

import { SimpleEditor } from '@/components/tiptap-templates/simple/simple-editor'
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";


export interface PostFormData {
  title: string;
  slug: string;
  content: JSONContent | string;
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
  const [content, setContent] = useState<JSONContent | string>(initialData?.content ?? "");
  const [excerpt, setExcerpt] = useState(initialData?.excerpt ?? "");
  const [published, setPublished] = useState(initialData?.published ?? true);

  const generateSlug = () => {
    if (!title.trim()) return;
    setSlug(
      title
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, "")
        .replace(/[\s_]+/g, "-")
        .replace(/-+/g, "-"),
    );
  };

  const handleSubmit = async (e: SubmitEvent) => {
    e.preventDefault();
    if (!title.trim() || !slug.trim() || content === "" || (typeof content === "string" && !content.trim())) return;

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
        <Button form="post-form" type="submit" disabled={isSubmitting}>
          {isSubmitting
            ? mode === "create"
              ? "Creating…"
              : "Saving…"
            : mode === "create"
              ? "Create Post"
              : "Save Changes"}
        </Button>
      </div>

      <form id="post-form" onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:gap-6">
            <div className="flex flex-1 flex-col gap-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Post title"
                required
              />
            </div>
            <div className="flex flex-col gap-2 sm:w-36">
              <Label>Status</Label>
              <Badge
                variant={published ? "default" : "secondary"}
                className="cursor-pointer px-3 py-1 text-sm"
                onClick={() => setPublished((p) => !p)}
              >
                {published ? "Published" : "Unpublished"}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="slug">Slug</Label>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={generateSlug} disabled={!title.trim()}>
              Generate
            </Button>
            <Input
              id="slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              placeholder="post-slug"
              required
              className="flex-1"
            />
          </div>
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

        <div className="flex flex-col gap-2">
          <Label htmlFor="content">Content</Label>
          <SimpleEditor
            content={content}
            onUpdate={setContent}
          />
        </div>
      </form>
    </div>
  );
}
