import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react({ fastRefresh: false })], // slå av react-refresh
  server: {
    port: 5199,
    strictPort: true,
    host: "127.0.0.1",
    hmr: false, // slå av HMR => ingen /@vite/client lenger
  },
});
