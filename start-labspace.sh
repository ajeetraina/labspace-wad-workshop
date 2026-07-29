#!/usr/bin/env bash
#
# start-labspace.sh — launch the "Securing the Agentic Stack" labspace locally.
#
# A labspace is a fully-packaged playground for labs, workshops and trainings.
# It runs locally in Docker and serves the step-by-step guide in your browser.
#
# Usage:
#   bash start-labspace.sh          # start (foreground)
#   bash start-labspace.sh down     # stop and clean up
#
set -euo pipefail

PORT=3030
COMPOSE_FILE="compose.yaml"

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker is not installed. Install Docker Desktop first:"
  echo "   https://www.docker.com/products/docker-desktop/"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "❌ Docker is not running. Start Docker Desktop and try again."
  exit 1
fi

if [[ "${1:-up}" == "down" ]]; then
  echo "🛑 Stopping labspace…"
  docker compose -p labspace -f "$COMPOSE_FILE" down
  exit 0
fi

echo "🐳 Starting the Securing the Agentic Stack labspace…"
docker compose -p labspace -f "$COMPOSE_FILE" up -d

echo ""
echo "✅ Labspace is starting. Open the lab in your browser:"
echo ""
echo "      👉  http://localhost:${PORT}"
echo ""
echo "   (It may take a few seconds for the content to become available.)"
echo ""
echo "   The full workshop is also hosted at https://dockerworkshop.vercel.app/"
echo ""
echo "   To stop it later:  bash start-labspace.sh down"
