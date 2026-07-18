#!/bin/bash
source .env  # load SLACK_WEBHOOK_URL locally; in CI this comes from secrets instead

docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
exit_code=$?
docker compose -f docker-compose.test.yml down

if [ $exit_code -eq 0 ]; then
    message="Tests passed for Project 3"
else
    message="Tests failed for Project 3"
fi

curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"$message\"}" \
    "$SLACK_WEBHOOK_URL"

exit $exit_code