FROM node:22-bookworm-slim

WORKDIR /app

# npm ci instala las versiones del package-lock.json.
COPY package.json package-lock.json ./
RUN npm ci

COPY --chown=node:node . .
RUN chown node:node /app

USER node
EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0", "--port", "3000"]
