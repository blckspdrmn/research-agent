FROM node:24-slim AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-slim AS runner
WORKDIR /app
# 本番用であることを NODE_ENVで明示: https://nodejs.org/learn/getting-started/nodejs-the-difference-between-development-and-production
# 外部から接続できるように0.0.0.0
ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000
# nodeのDockerイメージに含まれるnodeユーザーを用いる
COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public
USER node
EXPOSE 3000
# https://nextjs.org/docs/pages/api-reference/config/next-config-js/output#automatically-copying-traced-files
CMD ["node", "server.js"]
