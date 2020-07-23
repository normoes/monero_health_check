ARG ALPINE_VERSION="${ALPINE_VERSION:-3.12}"
ARG PYTHON_VERSION="${PYTHON_VERSION:-3.7}"
FROM python:${PYTHON_VERSION}-alpine${ALPINE_VERSION}

COPY . /data

WORKDIR "/data"

RUN apk add --no-cache git \
    && python -m pip install --upgrade -r requirements.txt \
    && chmod +x /data/entrypoint.sh

ENV USER_ID=1000
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

# ENTRYPOINT ["gunicorn"]
#
# CMD ["--workers", "3", "--bind", "0.0.0.0:$PORT", "wsgi:app"]
