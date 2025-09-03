#!/usr/bin/env bash
set -euo pipefail

CSV=${1:-templates.csv}

: "${ETRNL_PRIVATE_KEY:?set ETRNL_PRIVATE_KEY}"
: "${FRONTEND_ORIGIN:?set FRONTEND_ORIGIN (e.g., https://app.example.com)}"
APP_NAME="${APP_NAME:-Shop Frontend}"
USE_TAMPER="${USE_TAMPER:-0}"   # 0 = cmac, 1 = tt
DRY_RUN="${DRY_RUN:-0}"

api() {
  local method="$1"; shift
  local url="$1"; shift
  curl -sS -X "$method" "$url" \
    -H "API-Key: ${ETRNL_PRIVATE_KEY}" \
    -H "Content-Type: application/json" "$@"
}

find_group_id() {
  local name="$1"; local url="$2"
  local resp
  resp="$(api GET 'https://third-party.etrnl.app/v1/url-groups')"
  echo "$resp" | jq -r --arg n "$name" --arg u "$url" '
    .groups // [] | map(select((.name==$n) and (.customUrl==$u))) | .[0].id // empty
  '
}

create_group() {
  local name="$1"; local template_id="$2"; local version="$3"; local sku="$4"
  local custom_url
  if [ "$USE_TAMPER" = "1" ]; then
    custom_url="${FRONTEND_ORIGIN}/scan/{tagId}?enc={enc}&tt={tt}&eCode={eCode}&t=${template_id}"
  else
    custom_url="${FRONTEND_ORIGIN}/scan/{tagId}?enc={enc}&cmac={cmac}&eCode={eCode}&t=${template_id}"
  fi

  # Reuse if it already exists
  local existing
  existing="$(find_group_id "$name" "$custom_url")"
  if [ -n "$existing" ]; then
    echo "$existing"
    return
  fi

  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY: would create group name='$name' url='$custom_url'" >&2
    echo "DRY_GROUP_ID"
    return
  fi

  local payload resp ok gid
  payload="$(jq -nc --arg name "$name" --arg app "$APP_NAME" --arg url "$custom_url" \
    '{name:$name, appName:$app, customUrl:$url}')"
  resp="$(api POST 'https://third-party.etrnl.app/v1/url-groups' -d "$payload")"
  ok="$(echo "$resp" | jq -r '.success')"
  if [ "$ok" != "true" ]; then
    echo "ERROR creating group: $resp" >&2
    return 1
  fi
  gid="$(echo "$resp" | jq -r '.group.id // .group.groupId // .group.ID // empty')"
  if [ -z "$gid" ]; then
    # Fallback: fetch by name+url
    gid="$(find_group_id "$name" "$custom_url")"
  fi
  echo "$gid"
}

queue_meta() {
  local group_id="$1"; local display_name="$2"; local template_id="$3"; local version="$4"; local sku="$5"
  [ "$DRY_RUN" = "1" ] && { echo "DRY: would queue meta for group=$group_id"; return; }
  local meta payload resp ok
  meta="$(jq -nc --arg templateId "$template_id" --arg version "$version" --arg sku "$sku" \
           '{templateId:$templateId, version:$version, sku:$sku}')"
  payload="$(jq -nc --arg dn "$display_name" --arg tm "$meta" '{displayName:$dn, tagMetadata:$tm}')"
  resp="$(api POST "https://third-party.etrnl.app/v1/url-groups/${group_id}/queue" -d "$payload")"
  ok="$(echo "$resp" | jq -r '.success')"
  if [ "$ok" != "true" ]; then
    echo "WARN queue meta failed group=$group_id resp=$resp" >&2
  fi
}

# CSV header: template_id,display_name,version,sku
tail -n +2 "$CSV" | while IFS=, read -r template_id display_name version sku; do
  template_id="${template_id//[$'\r\n']}"; [ -z "$template_id" ] && continue
  display_name="${display_name//[$'\r\n']}"
  version="${version//[$'\r\n']}"
  sku="${sku//[$'\r\n']}"
  echo "=== $display_name ($version) ==="
  gid="$(create_group "$display_name" "$template_id" "$version" "$sku")"
  echo "URL Group ID: $gid"
  queue_meta "$gid" "$display_name" "$template_id" "$version" "$sku"
done
