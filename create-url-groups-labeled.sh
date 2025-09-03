#!/usr/bin/env bash
set -euo pipefail

CSV=${1:-templates.csv}

: "${ETRNL_PRIVATE_KEY:?set ETRNL_PRIVATE_KEY}"
: "${FRONTEND_ORIGIN:?set FRONTEND_ORIGIN (e.g., https://app.example.com)}"

# ---- Configurable labels ----
APP_NAME="${APP_NAME:-Shop Frontend}"     # Shown in ETRNL
ENV_LABEL="${ENV_LABEL:-DEV}"             # e.g., DEV, STAGE, PROD, LAN
USE_TAMPER="${USE_TAMPER:-1}"             # 1 = tt, 0 = cmac
PARAM_STYLE="${PARAM_STYLE:-long}"        # long -> enc/cmac, short -> e/c
ADD_HASH="${ADD_HASH:-1}"                 # append short hash of the customUrl to name (helps uniqueness)
DRY_RUN="${DRY_RUN:-0}"

# ---- Validate & normalize ----
case "$USE_TAMPER" in 0|1) ;; *) echo "ERROR: USE_TAMPER must be 0 or 1"; exit 1;; esac
case "$PARAM_STYLE" in long|short) ;; *) echo "ERROR: PARAM_STYLE must be long or short"; exit 1;; esac
if ! printf '%s' "$FRONTEND_ORIGIN" | grep -Eq '^https?://'; then
  echo "ERROR: FRONTEND_ORIGIN must start with http(s)://"; exit 1
fi
FRONTEND_ORIGIN="${FRONTEND_ORIGIN%/}"

enc_key="enc"; mac_key="cmac"
[ "$PARAM_STYLE" = "short" ] && { enc_key="e"; mac_key="c"; }

origin_label="$(printf '%s' "$FRONTEND_ORIGIN" | sed -E 's#^https?://##; s#/$##')"
mode_label=$([ "$USE_TAMPER" = "1" ] && echo "tt" || echo "$mac_key")

api() {
  local method="$1"; shift
  local url="$1"; shift
  curl -sS -X "$method" "$url" \
    -H "API-Key: ${ETRNL_PRIVATE_KEY}" \
    -H "Content-Type: application/json" "$@"
}

create_group() {
  local name="$1" template_id="$2" version="$3" sku="$4"

  # Build customUrl
  local custom_url
  if [ "$USE_TAMPER" = "1" ]; then
    custom_url="${FRONTEND_ORIGIN}/scan/{tagId}?${enc_key}={enc}&tt={tt}&eCode={eCode}&t=${template_id}"
  else
    custom_url="${FRONTEND_ORIGIN}/scan/{tagId}?${enc_key}={enc}&${mac_key}={cmac}&eCode={eCode}&t=${template_id}"
  fi

  # Validate that '=' signs exist
  case "$custom_url" in *"${enc_key}="* ) : ;;  *) echo "ERROR: ${enc_key} missing '='"; exit 1;; esac
  if [ "$USE_TAMPER" = "1" ]; then
    case "$custom_url" in *"tt="* ) : ;; *) echo "ERROR: tt missing '='"; exit 1;; esac
  else
    case "$custom_url" in *"${mac_key}="* ) : ;; *) echo "ERROR: ${mac_key} missing '='"; exit 1;; esac
  fi
  case "$custom_url" in *"eCode="* ) : ;; *) echo "ERROR: eCode missing '='"; exit 1;; esac
  case "$custom_url" in *"t="* ) : ;; *) echo "ERROR: t missing '='"; exit 1;; esac

  # Build a descriptive name
  # Base name from CSV display_name (already includes athlete and version is provided separately)
  local pretty_ver="$version"
  [ -z "$pretty_ver" ] && pretty_ver="n/a"

  # Optional short hash of URL (macOS has `md5`; Linux often has `md5sum`)
  local hash=""
  if [ "$ADD_HASH" = "1" ]; then
    if command -v md5 >/dev/null 2>&1; then
      hash="$(printf '%s' "$custom_url" | md5 | cut -c1-6)"
    elif command -v md5sum >/dev/null 2>&1; then
      hash="$(printf '%s' "$custom_url" | md5sum | cut -c1-6)"
    else
      hash="nohash"
    fi
  fi

  local label_suffix="[${ENV_LABEL} ${origin_label}|${mode_label}|${enc_key}${ADD_HASH:+|#${hash}}]"
  local group_name="${name} — ${pretty_ver} ${label_suffix}"

  echo "Name:      $group_name"
  echo "customUrl: $custom_url"

  if [ "$DRY_RUN" = "1" ]; then
    echo "DRY: would create URL Group"
    echo "DRY_GROUP_ID"
    return 0
  fi

  # Create group
  local payload resp ok gid
  payload="$(jq -nc --arg app "$APP_NAME" --arg name "$group_name" --arg url "$custom_url" \
    '{appName:$app, name:$name, customUrl:$url}')"
  resp="$(api POST 'https://third-party.etrnl.app/v1/url-groups' -d "$payload")"
  ok="$(echo "$resp" | jq -r '.success')"
  if [ "$ok" != "true" ]; then
    echo "ERROR creating group: $resp" >&2
    return 1
  fi
  gid="$(echo "$resp" | jq -r '.group.id // .group.groupId // .group.ID // empty')"

  # Queue programmer metadata (keeps the template hint on the ETRNL side)
  local meta payload2
  meta="$(jq -nc --arg templateId "$template_id" --arg version "$version" --arg sku "$sku" \
          '{templateId:$templateId, version:$version, sku:$sku}')"
  payload2="$(jq -nc --arg dn "$group_name" --arg tm "$meta" '{displayName:$dn, tagMetadata:$tm}')"
  resp="$(api POST "https://third-party.etrnl.app/v1/url-groups/${gid}/queue" -d "$payload2")" || true

  echo "URL Group ID: $gid"
}

# CSV header: template_id,display_name,version,sku
tail -n +2 "$CSV" | while IFS=, read -r template_id display_name version sku; do
  template_id="${template_id//[$'\r\n']}"; [ -z "$template_id" ] && continue
  display_name="${display_name//[$'\r\n']}"
  version="${version//[$'\r\n']}"
  sku="${sku//[$'\r\n']}"
  echo "=== $display_name ($version) ==="
  create_group "$display_name" "$template_id" "$version" "$sku"
done
