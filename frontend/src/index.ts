import { serve } from "bun";
import index from "./index.html";

const server = serve({
  routes: {
    "/*": index,

    "/health": {
      async GET() {
        return Response.json({
          message: "ok",
        });
      },
    },
  },

  development: process.env.NODE_ENV !== "production" && {
    hmr: true,
    console: true,
  },
});

console.log(`🚀 Server running at ${server.url}`);
