import { useParams, Link } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { usePostBySlug } from "@/lib/api";
import { DefaultLayout } from "@/layouts/DefaultLayout";
import { renderPostContent } from "@/lib/tiptap-renderer";

export function PostPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: post, isLoading, error } = usePostBySlug(slug!);

  return (
    <DefaultLayout>
      <div className="mb-6">
        <Link
          to="/"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← Back to posts
        </Link>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Loading post…</p>}
      {error && <p className="text-sm text-red-500">{error.message}</p>}

      {post && (
        <article className="space-y-6">
          <time className="mb-4 block text-sm text-muted-foreground">
            {new Date(post.created_at).toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </time>
          <div className="space-y-3">
            {!post.published && (
              <Badge variant="secondary">Unpublished preview</Badge>
            )}
            <h1 className="text-3xl font-bold">{post.title}</h1>
          </div>
          <div className="max-w-none">
            {renderPostContent(post.content)}
          </div>
        </article>
      )}
    </DefaultLayout>
  );
}

export default PostPage;
