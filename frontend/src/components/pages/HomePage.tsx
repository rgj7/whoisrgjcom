const posts = [
  { title: "Getting Started With Something New", date: "May 10, 2025", excerpt: "A placeholder post about kicking off a new project and the lessons learned along the way." },
  { title: "Thoughts On Design Systems", date: "May 5, 2025", excerpt: "Why consistency matters and how a well-built design system saves time at scale." },
  { title: "Building In Public", date: "Apr 28, 2025", excerpt: "The highs and lows of sharing your work openly and what the community teaches you." },
  { title: "The Art of Code Reviews", date: "Apr 20, 2025", excerpt: "How to give feedback that improves code without discouraging the author." },
  { title: "Rethinking Productivity", date: "Apr 12, 2025", excerpt: "Why doing less often leads to better outcomes than chasing busyness." },
];

export function HomePage() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        {/* Blog Posts — 2 columns */}
        <div className="space-y-6 lg:col-span-2">
          <h2 className="text-xl font-semibold">Latest Posts</h2>
          {posts.map((post) => (
            <article key={post.title} className="space-y-1 border-b pb-4">
              <h3 className="font-medium">{post.title}</h3>
              <time className="text-xs text-muted-foreground">{post.date}</time>
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
