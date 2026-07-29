#!/usr/bin/env bash
#
# start-labspace.sh — launch the "Securing the Agentic Stack" labspace locally.
#
# Usage:
#   bash start-labspace.sh          # start
#   bash start-labspace.sh down     # stop and clean up
#
set -euo pipefail

PORT=3030
COMPOSE_FILE="compose.yaml"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed. Install Docker Desktop first:"
  echo "  https://www.docker.com/products/docker-desktop/"
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Start Docker Desktop and try again."
  exit 1
fi

if [[ "${1:-up}" == "down" ]]; then
  echo "Stopping labspace..."
  docker compose -p labspace -f "$COMPOSE_FILE" down -v
  exit 0
fi

echo "Starting the Securing the Agentic Stack labspace..."
docker compose -p labspace -f "$COMPOSE_FILE" up -d

cat <<EOF

  Labspace is starting. Open it at:

      http://localhost:${PORT}

  The SDLC services take a little longer:

      Gitea      http://git.dockerlabs.xyz     (moby / moby1234)
      Registry   http://registry.dockerlabs.xyz

  To stop:  bash start-labspace.sh down

EOF
