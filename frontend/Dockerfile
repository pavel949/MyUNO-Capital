# MyUNO Capital — Frontend (Next.js 14) development image
FROM node:20-alpine

WORKDIR /app

# Install dependencies first for better layer caching
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the source
COPY . .

ENV NODE_ENV=development
EXPOSE 3000

# Boot the dev server directly (no separate build needed to run)
CMD ["npm", "run", "dev"]
