#!/usr/bin/env bash
# Sends N requests and shows which container served each one.
URL=${1:-http://localhost}
N=${2:-12}
for i in $(seq 1 "$N"); do
  echo -n "Request $i -> "
  curl -s "$URL/" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['instance'], '| total_hits =', d['total_hits'])"
done
echo; echo "Per-instance stats:"; curl -s "$URL/stats"; echo
