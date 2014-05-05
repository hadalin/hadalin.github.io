#!/bin/bash

set -e

rake test

export CFZ=$1
export CFE=$2
export CFK=$3
SUCCESS=$(curl -X POST "https://api.cloudflare.com/client/v4/zones/${CFZ}/purge_cache" \
     -H "X-Auth-Email: ${CFE}" \
     -H "X-Auth-Key: ${CFK}" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}' \
     | jq '.success')

if [ "$SUCCESS" != "true" ]; then
    exit 1
fi
