FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
COPY packages/api-client ./packages/api-client
COPY web-concepts-02 ./web-concepts-02
RUN npm ci --no-audit --no-fund && npm run build
FROM caddy:2-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/web-concepts-02/dist /srv
