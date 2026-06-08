#!/usr/bin/env bash
set -Eeuo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose-prod.yml}"
ENV_FILE="${ENV_FILE:-.env.prod}"
SERVICE_NAME="${POSTGRES_SERVICE:-postgres}"
BACKUP_DIR="${BACKUP_DIR:-backups/postgres}"
RCLONE_REMOTE="${RCLONE_REMOTE:-ftpbackup:whoisrgjcom-pg}"
LOCAL_KEEP_RECENT="${LOCAL_KEEP_RECENT:-5}"
PROJECT_NAME="${PROJECT_NAME:-whoisrgjcom}"

log() { printf '[%s] %s\n' "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" "$*"; }
fail() { printf 'Error: %s\n' "$*" >&2; exit 1; }

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Missing required command: $1"
}

require_cmd docker
require_cmd gzip
require_cmd sha256sum
require_cmd rclone
require_cmd sed
require_cmd find
require_cmd sort
require_cmd tail
require_cmd xargs

[[ -f "$COMPOSE_FILE" ]] || fail "Compose file not found: $COMPOSE_FILE"
[[ -f "$ENV_FILE" ]] || fail "Environment file not found: $ENV_FILE"

# Load POSTGRES_USER / POSTGRES_DB for pg_dump without printing secrets.
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required in $ENV_FILE}"
: "${POSTGRES_DB:?POSTGRES_DB is required in $ENV_FILE}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date -u +'%Y%m%dT%H%M%SZ')"
BASENAME="${PROJECT_NAME}-${POSTGRES_DB}-${TIMESTAMP}.sql.gz"
TMP_SQL="$(mktemp "${BACKUP_DIR}/.dump-${TIMESTAMP}.XXXXXX.sql")"
BACKUP_PATH="${BACKUP_DIR}/${BASENAME}"
CHECKSUM_FILE="${BACKUP_DIR}/latest.sha256"

cleanup() {
  rm -f "$TMP_SQL"
}
trap cleanup EXIT

compose=(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

log "Creating PostgreSQL dump from service '$SERVICE_NAME'..."
"${compose[@]}" exec -T "$SERVICE_NAME" pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  | sed -E \
      -e '/^-- Started on:/d' \
      -e '/^-- Completed on:/d' \
      -e '/^\\restrict /d' \
      -e '/^\\unrestrict /d' \
  > "$TMP_SQL"

CURRENT_SHA="$(sha256sum "$TMP_SQL" | awk '{print $1}')"
PREVIOUS_SHA=""
if [[ -f "$CHECKSUM_FILE" ]]; then
  PREVIOUS_SHA="$(awk '{print $1}' "$CHECKSUM_FILE")"
fi

if [[ -n "$PREVIOUS_SHA" && "$CURRENT_SHA" == "$PREVIOUS_SHA" ]]; then
  log "Database dump is unchanged since the last successful remote backup; skipping save/upload."
  exit 0
fi

log "Database changed; writing compressed backup: $BACKUP_PATH"
gzip -n -c "$TMP_SQL" > "$BACKUP_PATH"

log "Uploading backup via rclone: $RCLONE_REMOTE"
rclone copy "$BACKUP_PATH" "$RCLONE_REMOTE"

printf '%s  %s\n' "$CURRENT_SHA" "$BASENAME" > "$CHECKSUM_FILE"
log "Updated checksum state: $CHECKSUM_FILE"

if [[ "$LOCAL_KEEP_RECENT" =~ ^[0-9]+$ && "$LOCAL_KEEP_RECENT" -gt 0 ]]; then
  log "Keeping the newest $LOCAL_KEEP_RECENT local backup(s)."
  find "$BACKUP_DIR" -maxdepth 1 -type f -name '*.sql.gz' -print \
    | sort \
    | head -n -"$LOCAL_KEEP_RECENT" \
    | xargs -r rm -f
else
  log "Skipping local retention cleanup because LOCAL_KEEP_RECENT is not a positive integer: $LOCAL_KEEP_RECENT"
fi

log "Backup complete."
