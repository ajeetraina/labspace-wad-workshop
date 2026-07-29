# Lab 2 starting point — DHI base with attestations
# Build: docker buildx build --sbom=true --provenance=mode=max -t myapp:v1 --push .

FROM docker/hardened-node:20-alpine

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
