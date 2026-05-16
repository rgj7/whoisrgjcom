import { Link } from "react-router-dom";
import { usePosts } from "../lib/api";

export function HomePage() {
  const { data: posts, isLoading, error } = usePosts();

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Blog Posts — 2 columns */}
        <div className="space-y-6 lg:col-span-2">
          <h2 className="text-xl font-semibold">Latest Posts</h2>
          {isLoading && <p className="text-sm text-muted-foreground">Loading posts…</p>}
          {error && <p className="text-sm text-red-500">{error.message}</p>}
          {!isLoading && !error && !posts?.length && (
            <p className="text-sm text-muted-foreground">No posts yet.</p>
          )}
          {posts?.map((post) => (
            <article key={post.id} className="space-y-1 border-b pb-4">
              <h3 className="font-medium">
                <Link
                  to={`/posts/${post.slug}`}
                  className="hover:underline"
                >
                  {post.title}
                </Link>
              </h3>
              <time className="text-xs text-muted-foreground">
                {new Date(post.created_at).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </time>
              <p className="text-sm text-muted-foreground">{post.excerpt}</p>
            </article>
          ))}
        </div>

        {/* Widgets — 1 column */}
        <aside className="space-y-6">
          <div className="rounded-lg border p-4">
            <h2 className="mb-2 text-sm font-semibold">About</h2>
            <p className="text-sm text-muted-foreground">
              Placeholder bio and introduction text goes here.
            </p>
          </div>
          <div className="rounded-lg border p-4">
            <h2 className="mb-2 text-sm font-semibold">Categories</h2>
            <ul className="space-y-1 text-sm text-muted-foreground">
              <li>Technology</li>
              <li>Design</li>
              <li>Travel</li>
              <li>Gaming</li>
            </ul>
          </div>
          <div className="rounded-lg border p-4">
            <h2 className="mb-2 text-sm font-semibold">Tags</h2>
            <div className="flex flex-wrap gap-2">
              {[
                "react",
                "typescript",
                "css",
                "blogging",
                "productivity",
                "design",
              ].map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-secondary px-2 py-1 text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default HomePage;
