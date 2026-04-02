#! /bin/sh

cd ui && npm install -g "$(jq -r '.packageManager' package.json)" && pnpm install && pnpm run build
