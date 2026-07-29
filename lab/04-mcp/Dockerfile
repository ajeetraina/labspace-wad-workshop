# Lab 4 — MCP server on Docker Hardened Images
# Two-stage: dev variant for build, distroless runtime for prod.
# Replace DHI_PREFIX with: dhi.io/  (free) or YOUR_ORG/dhi-  (paid)

ARG DHI_PREFIX=dhi.io/

###########################################################
# Stage: build — DHI Python dev variant (has pip + shell)
###########################################################
FROM ${DHI_PREFIX}python:3.12-slim-dev AS build

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --target /app/deps

###########################################################
# Stage: final — DHI Python distroless runtime
#   - No shell
#   - No pip
#   - No curl or wget
###########################################################
FROM ${DHI_PREFIX}python:3.12-slim AS final

ENV PYTHONPATH=/app/deps
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY --from=build /app/deps ./deps
COPY ./src ./src

EXPOSE 8080
CMD ["python", "src/mcp_server.py"]
