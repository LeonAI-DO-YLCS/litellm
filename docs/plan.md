# LiteLLM Network-Only Docker Deployment Plan

## Tasks

- ✅ Create deployment requirements for a LAN and Tailscale restricted LiteLLM proxy.
- ✅ Decide on an implementation that uses a dedicated compose stack and Docker-aware firewall rules.
- ✅ Add deployment files:
  - `docker-compose.network-only.yml`
  - `docker/litellm.network-only.yaml`
  - `docker/restrict-litellm-port.sh`
- ✅ Update Docker documentation with deployment and rollback steps.
- ✅ Start the stack, apply firewall rules, and verify health and listening state.

## Verification

- ✅ Compose config renders successfully.
- ✅ Docker services are healthy.
- ✅ Local health endpoint responds on `127.0.0.1:4000`.
- ✅ LAN health endpoint responds on `192.168.1.8:4000`.
- ✅ Tailscale health endpoint responds on `100.95.142.89:4000`.
- ✅ Firewall chain is present in `DOCKER-USER` and includes the expected allow and drop rules.
