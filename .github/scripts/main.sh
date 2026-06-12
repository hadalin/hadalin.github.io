#!/bin/bash

set -e

SUCCESS=$(curl -sf -X POST "https://api.cloudflare.com/client/v4/zones/${CFZ}/purge_cache" \
     -H "Authorization: Bearer ${CFK}" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}' \
     | jq '.success')

if [ "$SUCCESS" != "true" ]; then
    exit 1
fi
