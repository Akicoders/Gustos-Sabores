// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  env: {
    schema: {
      PUBLIC_API_URL: new URL('').toString(),
    }
  }
});
