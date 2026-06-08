#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
SERVICE_NAME="${POSTGRES_SERVICE:-postgres}"
FORCE="${FORCE:-0}"

fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }
log() { printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }

usage() {
  cat <<USAGE
Usage: $0 path/to/backup.sql.gz

Restores a gzip-compressed plain SQL PostgreSQL dump into the configured Docker Compose PostgreSQL service.

Overrides:
  COMPOSE_FILE=docker-compose-dev.yml
  ENV_FILE=.env
  POSTGRES_SERVICE=postgres
  FORCE=1                 Skip confirmation prompt
USAGE
}

[[ $# -eq 1 ]] || { usage; exit 2; }
BACKUP_PATH="$1"

command -v docker >/dev/null 2>&1 || fail "Missing required command: docker"
command -v gunzip >/dev/null 2>&1 || fail "Missing required command: gunzip"

[[ -f "$BACKUP_PATH" ]] || fail "Backup file not found: $BACKUP_PATH"
[[ -f "$COMPOSE_FILE" ]] || fail "Compose file not found: $COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || fail "Environment file not found: $ENV_FILE"

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required in $ENV_FILE}"
: "${POSTGRES_DB:?POSTGRES_DB is required in $ENV_FILE}"

if [[ "$FORCE" != "1" ]]; then
  cat <<WARNING
You are about to restore:
  $BACKUP_PATH

Into database:
  $POSTGRES_DB

Using:
  $COMPOSE_FILE
  $ENV_FILE

This may drop/replace existing database objects.
WARNING
  read -r -p "Type RESTORE to continue: " confirmation
  [[ "$confirmation" == "RESTORE" ]] || fail "Restore cancelled."
fi

compose=(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

log "Restoring backup into service '$SERVICE_NAME' database '$POSTGRES_DB'..."
gunzip -c "$BACKUP_PATH" | "${compose[@]}" exec -T "$SERVICE_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1
log "Restore complete."
