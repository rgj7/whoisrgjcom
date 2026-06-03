import { Link } from "react-router-dom";
import { usePosts, useSocialLinks } from "@/lib/api";
import { DefaultLayout } from "@/layouts/DefaultLayout";

export function HomePage() {
  const { data: posts, isLoading, error } = usePosts();
  const {
    data: socialLinks,
    isLoading: isLoadingSocialLinks,
    error: socialLinksError,
  } = useSocialLinks();

  return (
    <DefaultLayout>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Blog Posts — 2 columns */}
        <div className="space-y-6 lg:col-span-2">
          <div className="flex items-center gap-3 mb-6">
            <span className="block h-6 w-1 rounded-full bg-foreground" />
            <h2 className="text-2xl font-semibold">Latest Posts</h2>
            <span className="h-px flex-1 bg-border" />
          </div>
          {isLoading && <p className="text-sm text-muted-foreground">Loading posts…</p>}
          {error && <p className="text-sm text-red-500">{error.message}</p>}
          {!isLoading && !error && !posts?.items?.length && (
            <p className="text-sm text-muted-foreground">No posts yet.</p>
          )}
          {posts?.items?.map((post) => (
            <article key={post.id} className="space-y-2 border-b pb-6">
              <time className="text-xs text-muted-foreground">
                {new Date(post.created_at).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </time>
              <h3 className="text-xl font-semibold">
                <Link
                  to={`/posts/${post.slug}`}
                  className="hover:underline"
                >
                  {post.title}
                </Link>
              </h3>
              <p className="text-sm text-muted-foreground">{post.excerpt}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded bg-secondary px-2 py-1 text-xs"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>

        {/* Widgets — 1 column */}
        <aside className="space-y-6">
          <div className="rounded-lg border p-4">
            <h2 className="mb-2 text-sm font-semibold">About</h2>
            <p className="text-sm text-muted-foreground">
              Hey there! My name is Raul. I am a software engineer, formerly Apple, Amazon, Hulu/Disney. I am a chronic puzzle seeker, an aspiring world traveler, and a sports fanatic and an avid gamer.
            </p>
          </div>
          <div className="rounded-lg border p-4">
            <h2 className="mb-2 text-sm font-semibold">Find Me On</h2>
            {isLoadingSocialLinks && <p className="text-sm text-muted-foreground">Loading links…</p>}
            {socialLinksError && <p className="text-sm text-muted-foreground">Social links unavailable.</p>}
            {!isLoadingSocialLinks && !socialLinksError && !socialLinks?.links.length && (
              <p className="text-sm text-muted-foreground">No social links yet.</p>
            )}
            {!!socialLinks?.links.length && (
              <ul className="space-y-1 text-sm text-muted-foreground">
                {socialLinks.links.map((link) => (
                  <li key={link.id}>
                    <a
                      href={link.url}
                      target="_blank"
                      rel="noreferrer"
                      className="hover:text-foreground hover:underline"
                    >
                      {link.platform}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>
      </div>
    </DefaultLayout>
  );
}

export default HomePage;
