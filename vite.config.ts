import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs';
import {defineConfig, Plugin} from 'vite';

function apkServePlugin(): Plugin {
  return {
    name: 'apk-serve-plugin',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url && req.url.startsWith('/apk/') && req.url.endsWith('.apk')) {
          const cleanUrl = req.url.split('?')[0];
          const filePath = path.join(process.cwd(), 'public', cleanUrl);
          if (fs.existsSync(filePath)) {
            const fileName = path.basename(filePath);
            const stat = fs.statSync(filePath);
            res.writeHead(200, {
              'Content-Type': 'application/vnd.android.package-archive',
              'Content-Disposition': `attachment; filename="${fileName}"`,
              'Content-Length': stat.size,
              'Cache-Control': 'no-cache',
            });
            const stream = fs.createReadStream(filePath);
            stream.pipe(res);
            return;
          }
        }
        next();
      });
    },
  };
}

export default defineConfig(() => {
  return {
    plugins: [react(), tailwindcss(), apkServePlugin()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modifyâfile watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
      // Disable file watching when DISABLE_HMR is true to save CPU during agent edits.
      watch: process.env.DISABLE_HMR === 'true' ? null : {},
    },
  };
});
