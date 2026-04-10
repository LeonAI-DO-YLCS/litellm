# LiteLLM Network-Only Deployment Decisions

## ADR-001: Use a Dedicated Compose File

- Status: Accepted
- Context: The repository's default `docker-compose.yml` publishes additional services and a PostgreSQL port that are not needed for a network-restricted LiteLLM deployment on this host.
- Decision: Add a separate `docker-compose.network-only.yml` that runs only LiteLLM and an internal PostgreSQL service, with the database available only on the Docker network.
- Consequence: The deployment stays isolated from unrelated services and avoids port conflicts on `5432`.

## ADR-002: Restrict Inbound Access with Docker's `DOCKER-USER` Chain

- Status: Accepted
- Context: Docker-published ports bypass normal host `INPUT` filtering on many Linux setups, so restricting access in `INPUT` alone is unreliable.
- Decision: Apply source-based allow rules for loopback, LAN, and Tailscale CIDRs in a dedicated chain attached to `DOCKER-USER`, then drop other inbound traffic to LiteLLM port `4000`.
- Consequence: The access policy applies to Docker-published traffic consistently without changing the container image or app code.

## ADR-003: Keep Provider Configuration Out of This Task

- Status: Accepted
- Context: The current checked-in environment only guarantees a LiteLLM master key and does not define a provider API key.
- Decision: Deploy the proxy with DB-backed model management enabled and no hardcoded upstream model list.
- Consequence: The proxy and admin UI work immediately, and upstream models can be added later without changing the deployment shape.
