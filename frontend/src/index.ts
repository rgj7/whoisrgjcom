import { serve } from "bun";
import index from "./index.html";

const server = serve({
  routes: {
    "/images/*": async (req) => {
      const { pathname } = new URL(req.url);
      const file = Bun.file(`public${pathname}`);

      if (await file.exists()) {
        return new Response(file);
      }

      return new Response("Not Found", { status: 404 });
    },

    "/health": {
      async GET() {
        return Response.json({
          message: "ok",
        });
      },
    },

    "/*": index,
  },

  development: process.env.NODE_ENV !== "production" && {
    hmr: true,
    console: true,
  },
});

console.log(`🚀 Server running at ${server.url}`);
