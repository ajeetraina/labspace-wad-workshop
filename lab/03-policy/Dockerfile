# Lab 3 — CI policy enforcement
# Round 1: this standard base WILL FAIL the Scout policy gate (critical CVEs, no SBOM)
# Round 2: switch FROM to docker/hardened-node:24-debian13-dev / final pattern

FROM node:20

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
