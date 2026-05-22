import { useParams, Link } from "react-router-dom";
import { usePostBySlug } from "@/lib/api";
import { DefaultLayout } from "@/layouts/DefaultLayout";
import { renderPostContent } from "@/lib/tiptap-renderer";

export function PostPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: post, isLoading, error } = usePostBySlug(slug!);

  return (
    <DefaultLayout>
      <Link
        to="/"
        className="text-sm text-muted-foreground hover:text-foreground"
      >
        ← Back to posts
      </Link>

      {isLoading && <p className="text-sm text-muted-foreground">Loading post…</p>}
      {error && <p className="text-sm text-red-500">{error.message}</p>}

      {post && (
        <article className="space-y-4">
          <h1 className="text-3xl font-bold">{post.title}</h1>
          <time className="text-sm text-muted-foreground">
            {new Date(post.created_at).toLocaleDateString("en-US", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </time>
          <div className="max-w-none">
            {renderPostContent(post.content)}
          </div>
        </article>
      )}
    </DefaultLayout>
  );
}

export default PostPage;
