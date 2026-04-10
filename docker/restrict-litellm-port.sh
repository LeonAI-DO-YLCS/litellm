#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-apply}"
PORT="${LITELLM_PORT:-4000}"
LAN_CIDR="${LAN_CIDR:-192.168.1.0/24}"
TAILSCALE_CIDR="${TAILSCALE_CIDR:-100.64.0.0/10}"
TAILSCALE6_CIDR="${TAILSCALE6_CIDR:-fd7a:115c:a1e0::/48}"
CHAIN="LITELLM_${PORT}_FILTER"

need_root() {
  if [[ "${EUID}" -ne 0 ]]; then
    echo "Run as root: sudo $0 ${ACTION}" >&2
    exit 1
  fi
}

ensure_parent_chain() {
  local bin="$1"
  if ! "${bin}" -S DOCKER-USER >/dev/null 2>&1; then
    echo "DOCKER-USER chain not found for ${bin}. Start Docker first." >&2
    exit 1
  fi
}

attach_chain() {
  local bin="$1"
  "${bin}" -N "${CHAIN}" 2>/dev/null || true
  "${bin}" -F "${CHAIN}"
  "${bin}" -C DOCKER-USER -j "${CHAIN}" 2>/dev/null || "${bin}" -I DOCKER-USER 1 -j "${CHAIN}"
}

populate_ipv4_rules() {
  iptables -A "${CHAIN}" -p tcp --dport "${PORT}" -s 127.0.0.1/32 -j RETURN
  iptables -A "${CHAIN}" -p tcp --dport "${PORT}" -s "${LAN_CIDR}" -j RETURN
  iptables -A "${CHAIN}" -p tcp --dport "${PORT}" -s "${TAILSCALE_CIDR}" -j RETURN
  iptables -A "${CHAIN}" -p tcp --dport "${PORT}" -j DROP
  iptables -A "${CHAIN}" -j RETURN
}

populate_ipv6_rules() {
  if ! ip6tables -S DOCKER-USER >/dev/null 2>&1; then
    return
  fi

  ip6tables -N "${CHAIN}" 2>/dev/null || true
  ip6tables -F "${CHAIN}"
  ip6tables -C DOCKER-USER -j "${CHAIN}" 2>/dev/null || ip6tables -I DOCKER-USER 1 -j "${CHAIN}"
  ip6tables -A "${CHAIN}" -p tcp --dport "${PORT}" -s ::1/128 -j RETURN
  ip6tables -A "${CHAIN}" -p tcp --dport "${PORT}" -s "${TAILSCALE6_CIDR}" -j RETURN
  ip6tables -A "${CHAIN}" -p tcp --dport "${PORT}" -j DROP
  ip6tables -A "${CHAIN}" -j RETURN
}

remove_rules() {
  local bin="$1"
  if ! "${bin}" -S "${CHAIN}" >/dev/null 2>&1; then
    return
  fi

  while "${bin}" -C DOCKER-USER -j "${CHAIN}" >/dev/null 2>&1; do
    "${bin}" -D DOCKER-USER -j "${CHAIN}"
  done
  "${bin}" -F "${CHAIN}"
  "${bin}" -X "${CHAIN}"
}

show_status() {
  echo "iptables DOCKER-USER:"
  iptables -S DOCKER-USER
  if iptables -S "${CHAIN}" >/dev/null 2>&1; then
    echo
    echo "iptables ${CHAIN}:"
    iptables -S "${CHAIN}"
  fi

  if ip6tables -S DOCKER-USER >/dev/null 2>&1; then
    echo
    echo "ip6tables DOCKER-USER:"
    ip6tables -S DOCKER-USER
    if ip6tables -S "${CHAIN}" >/dev/null 2>&1; then
      echo
      echo "ip6tables ${CHAIN}:"
      ip6tables -S "${CHAIN}"
    fi
  fi
}

apply_rules() {
  ensure_parent_chain iptables
  attach_chain iptables
  populate_ipv4_rules

  if ip6tables -S DOCKER-USER >/dev/null 2>&1; then
    populate_ipv6_rules
  fi
}

need_root

case "${ACTION}" in
  apply)
    apply_rules
    show_status
    ;;
  remove)
    remove_rules iptables
    if ip6tables -S DOCKER-USER >/dev/null 2>&1; then
      remove_rules ip6tables
    fi
    show_status
    ;;
  status)
    show_status
    ;;
  *)
    echo "Usage: sudo $0 [apply|remove|status]" >&2
    exit 1
    ;;
esac
