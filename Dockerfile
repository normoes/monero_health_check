ARG ALPINE_VERSION="${ALPINE_VERSION:-3.12}"
ARG PYTHON_VERSION="${PYTHON_VERSION:-3.7}"
FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV USER_ID=1000

COPY . /data

WORKDIR "/data"

RUN apk add --no-cache --virtual .build_deps \
        gcc \
        linux-headers \
        libffi-dev \
        file \
        make \
    && apk add --no-cache \
        postgresql-dev \
        musl-dev \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir --upgrade -r /data/build_requirements.txt \
    && adduser -u "$USER_ID" -s /bin/false -D user \
    && chown -R user:user /data \
    && su user -s /bin/ash -c "pip-sync --user requirements.txt  --pip-args='--no-cache-dir'" \
    && chmod +x /data/entrypoint.sh \
    && apk del --no-cache .build_deps \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

ENV PATH /home/user/.local/bin:$PATH
USER user

ENV PORT=18091
ENV MONEROD_RPC_URL="127.0.0.1"
ENV MONEROD_RPC_PORT="18081"
ENV MONEROD_RPC_USER=""
ENV MONEROD_RPC_PASSWORD=""
ENV MONERO_WALLET_RPC_URL="127.0.0.1"
ENV MONERO_WALLET_RPC_PORT="18083"
ENV MONERO_WALLET_RPC_USER=""
ENV MONERO_WALLET_RPC_PASSWORD=""
ENV OFFSET=12
ENV OFFSET_UNIT="minutes"

ENTRYPOINT ["/data/entrypoint.sh"]
