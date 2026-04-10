# LiteLLM Network-Only Docker Deployment Requirements

## Goal

Run LiteLLM in Docker on this host so the proxy is reachable from:

- The local LAN
- The local Tailscale network
- The Windows host running this WSL environment

The deployment must not expose the LiteLLM proxy to arbitrary external internet clients.

## Functional Requirements

1. The LiteLLM proxy must run in Docker with a persistent database backend.
2. The proxy must listen on TCP port `4000`.
3. The proxy must be reachable from the current LAN subnet `192.168.1.0/24`.
4. The proxy must be reachable from the Tailscale CGNAT range `100.64.0.0/10`.
5. The proxy must remain reachable from local loopback so the Windows host can continue using `localhost` or the WSL IP.
6. The PostgreSQL service must not be published to the network.
7. The proxy must require a LiteLLM master key.
8. The deployment must expose a working health endpoint for verification.
9. The deployment must be repeatable with checked-in project files and a small number of host commands.

## Non-Goals

- Configuring a specific upstream model provider in this task
- Publishing LiteLLM to a public domain or reverse proxy
- Opening any inbound database port

## Acceptance Criteria

- `docker compose -f docker-compose.network-only.yml up -d --build` starts the proxy and database.
- `curl http://127.0.0.1:4000/health/liveliness` returns success after startup.
- The proxy port is reachable on the host LAN IP and Tailscale IP.
- Docker firewall rules restrict inbound access to loopback, the LAN subnet, and the Tailscale subnet for port `4000`.
- The deployment steps are documented in the repository.
