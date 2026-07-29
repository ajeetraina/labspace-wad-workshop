# Lab 1 starting point — standard Node.js image
# Run: docker scout cves node:20-alpine  (shows ~190 CVEs)
# Then change FROM to docker/hardened-node:20-alpine and re-scan

FROM node:20-alpine

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
