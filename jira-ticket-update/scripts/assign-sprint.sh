#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $(basename "$0") <TICKET_KEY> <SPRINT_NAME>

Assign a Jira ticket to a sprint using the jira CLI's built-in auth.

Arguments:
  TICKET_KEY   Jira ticket key (e.g., GENAI-167)
  SPRINT_NAME  Sprint name to match (e.g., "C2:26 Sprint 2")

Known board IDs (cached):
  GENAI -> 1700

The script looks up the board ID from the ticket's project key,
finds the sprint by name among active/future sprints, moves the
ticket, and verifies the assignment.

Examples:
  $(basename "$0") GENAI-167 "C2:26 Sprint 2"
  $(basename "$0") DEVOPS-456 "Sprint 14"
EOF
  exit 1
}

[[ $# -lt 2 ]] && usage

TICKET_KEY="$1"
SPRINT_NAME="$2"
PROJECT_KEY="${TICKET_KEY%%-*}"

lookup_cached_board_id() {
  case "$1" in
    GENAI) echo 1700 ;;
    *)     echo "" ;;
  esac
}

CACHED=$(lookup_cached_board_id "$PROJECT_KEY")
if [[ -n "$CACHED" ]]; then
  BOARD_ID="$CACHED"
  echo "Board ID for $PROJECT_KEY: $BOARD_ID (cached)"
else
  echo "Looking up board for project $PROJECT_KEY..."
  BOARD_JSON=$(jira request -M GET "/rest/agile/1.0/board?projectKeyOrId=$PROJECT_KEY&type=scrum")
  BOARD_ID=$(echo "$BOARD_JSON" | python3 -c "
import json, sys
data = json.load(sys.stdin)
values = data.get('values', [])
if not values:
    print('ERROR: No scrum board found for project $PROJECT_KEY', file=sys.stderr)
    sys.exit(1)
print(values[0]['id'])
")
  echo "Board ID for $PROJECT_KEY: $BOARD_ID"
fi

echo "Searching for sprint \"$SPRINT_NAME\" on board $BOARD_ID..."
SPRINT_JSON=$(jira request -M GET "/rest/agile/1.0/board/$BOARD_ID/sprint?state=active,future")
SPRINT_ID=$(echo "$SPRINT_JSON" | python3 -c "
import json, sys
target = '''$SPRINT_NAME'''
data = json.load(sys.stdin)
for s in data.get('values', []):
    if s['name'] == target:
        print(s['id'])
        sys.exit(0)
print('ERROR', file=sys.stderr)
names = [s['name'] for s in data.get('values', [])]
print(f'Sprint \"{target}\" not found. Available: {names}', file=sys.stderr)
sys.exit(1)
")

echo "Moving $TICKET_KEY to sprint $SPRINT_ID ($SPRINT_NAME)..."
jira request -M POST "/rest/agile/1.0/sprint/$SPRINT_ID/issue" "{\"issues\":[\"$TICKET_KEY\"]}"

VERIFY=$(jira request -M GET "/rest/agile/1.0/issue/$TICKET_KEY" --gjq "fields.sprint.name")
if [[ "$VERIFY" == "$SPRINT_NAME" ]]; then
  echo "Done. $TICKET_KEY is now in sprint: $VERIFY"
else
  echo "Warning: expected sprint \"$SPRINT_NAME\" but got \"$VERIFY\"" >&2
  exit 1
fi
