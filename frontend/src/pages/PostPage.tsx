import { useParams, Link } from "react-router-dom";
import { usePostBySlug } from "../lib/api";

export function PostPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: post, isLoading, error } = usePostBySlug(slug!);

  return (
    <div className="space-y-6">
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
          <div className="prose prose-sm dark:prose-invert max-w-none">
            {post.content.split("\n\n").map((paragraph, i) => (
              <p key={i} className="text-muted-foreground">
                {paragraph}
              </p>
            ))}
          </div>
        </article>
      )}
    </div>
  );
}

export default PostPage;
