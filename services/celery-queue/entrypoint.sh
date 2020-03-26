#!/bin/sh

flower -A tasks --persistent=True --db=/persistent/mydb --max-tasks=100000 --port=5555 --broker="$CELERY_BROKER_URL" --basic_auth="$FLOWER_USER":"$FLOWER_PASSWORD" &
celery -A tasks worker --loglevel=info
