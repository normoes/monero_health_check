#!/bin/ash

GUNICORN_CMD="gunicorn"
GUNICORN_OPTIONS="--workers 3 --bind 0.0.0.0:$PORT"
GUNICORN_APP="wsgi:app"

if [ -z "$@" ]; then
    set -- "$GUNICORN_CMD $GUNICORN_OPTIONS $GUNICORN_APP"
else
    set -- "$GUNICORN_CMD $GUNICORN_OPTIONS $@ $GUNICORN_APP"
fi

exec $@
