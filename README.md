# Monero health check

This is work in progress.

The `Monero health check` is a small webserver providing a REST API.

`Monero health check` provides information about the Monero daemon health.

**_Note_**:

There also is a docker image. Check it out: https://hub.docker.com/repository/docker/normoes/monero_health_check

Endpoints are:
* `/api/v1`
  - Combines results of all endpoints, returning everything.
* `/api/v1/monerod`
  - Gives basic information about the daemon, including `/api/v1/monerod/health`.
* `/api/v1/monerod/health`
  - Gives Monero daemon status from `get_info`.
* `/api/v1/last_block`
  - Gives basic information about the last block found on the Monero daemon, including `/api/v1/last_block/health`.
* `/api/v1/last_block/health`
  - Gives Monero dameon status based on the age of the last block.
* `/api/v1/health`
  - Combines health checks from all `/health` endpoints, returning an overall `status`.
  - In case one of the health checks fails, `status` will become `ERROR`, check `/api/v1` for details.

**_Note_**:

The core of this service is the [`monero_health`](https://github.com/normoes/monero_health) module, which uses [`python-monerorpc`](https://github.com/monero-ecosystem/python-monerorpc) to establish the RPC connection to the Monero daemon.

## Configuration

The Flask development server - not recommended for use in production - runs here:
```
    127.0.0.1:5000
```
**_Note_**:

The development server in `app.py` is configured with `host=0.0.0.0` in order to make it accessible from witihn the docker container.

The recommended way is to serve `Monero health check` using a real WSGI server like **gunicorn**.

The easiest way is to just start the docker container (`python3.7`, `alpine3.10`):
```
    docker-compose up --build
```

The `Monero health check` service can be found here:
```
    127.0.0.1:18091
```

### Monero daemon connection
The connection to the Monero dameon can be configured using environment variables (also see `docker-compose-template.yml`):

| environment variable | default value |
|----------------------|---------------|
| `MONEROD_RPC_URL` | `"127.0.0.1"` |
| `MONEROD_RPC_PORT` | `18081` |
| `MONEROD_RPC_USER` | `""` |
| `MONEROD_RPC_PASSWORD` | `""` |

**_Note_**:

The core of this service is the [`monero_health`](https://github.com/normoes/monero_health) module, which uses [`python-monerorpc`](https://github.com/monero-ecosystem/python-monerorpc) to establish the RPC connection to the Monero daemon.

**_Note_**:

Please also refer to [`monero_health`](https://github.com/normoes/monero_health)

### Last block age

`/api/v1/last_block/health` returns a `status` key.

This `status` shows whether the last block found on the daemon's blockchain is older than a pre-configured value:

| environment variable | default value |
|----------------------|---------------|
| `OFFSET` | `12` |
| `OFFSET_UNIT` | `"minutes"` |

I.e that the last block is considered out-of-date as soon as it becomes older than - in the default case - `12 [minutes]`.

In this case `status` will be `ERROR`, otherwise `status` is `OK`.

A `status` resulting in `ERROR` causes the overall `status` returned by requesting `/api/v1/health` to be `ERROR` as well.

**_Note_**:

Please also refer to [`monero_health`](https://github.com/normoes/monero_health)

### Daemon status

No configuration is needed.

The Monero RPC method used is:
* `hard_fork_info`

**_Note_**:

Please also refer to [`monero_health`](https://github.com/normoes/monero_health)

## Endpoints

The current version uses the API version
```
/api/v1
```

`v1` is the current version.

### Last block age

`/api/v1/last_block` returns the complete set of information about the last block on the daemon including a nested `health` key that contains the `status`:
```
{
    "result": {
        "block_recent": true,
        "block_recent_offset": "12",
        "block_recent_offset_unit": "minutes",
        "block_timestamp": "2020-01-07T14:57:52",
        "check_timestamp": "2020-01-07T14:58:07",
        "hash": "b105782d8e50d142d05abf0159d248a2898c09c3984cd69e144c8bfe7def0ee3",
        "health": {
            "status": "OK"
        }
    }
}
```

`/api/v1/last_block/health` returns the last block's `status` only:
```
{
    "result": {
        "status": "OK"
    }
}
```

### Daemon status

`/api/v1/monerod` returns some daemon information simply by calling the RPC method `hard_fork_info`. Here, as well, you will find a nested `health` key that contains the `status`:
```
{
    "result": {
        "health": {
            "status": "OK"
        },
        "version": 12
    }
}
```

`/api/v1/monerod/health` returns the daemon's `status` only:
```
{
    "result": {
        "status": "OK"
    }
}
```

### Combined Status

`/api/v1` checks every health endpoint possible and returns a complete list of all the possible information. Again, a nested `health` key contains the combined `status`:
```
{
    "result": {
        "health": {
            "status": "OK"
        },
        "last_block": {
            "block_recent": true,
            "block_recent_offset": 12,
            "block_recent_offset_unit": "minutes",
            "block_timestamp": "2020-01-07T14:58:14",
            "check_timestamp": "2020-01-07T15:06:37",
            "hash": "b105d4c44e0a4d7e0cadcf3997ee4947b895983341d05969d29c3c119c9bee08",
            "health": {
                "status": "OK"
            }
        },
        "monerod": {
            "health": {
                "status": "OK"
            },
            "version": 12
        }
    }
}
```

`/api/v1/health` returns the combined `status` only:
```
{
    "result": {
        "status": "OK"
    }
}
```

## Results

### Possible status values
**_Note_**:

For possible daemon `status` values, please also refer to [`monero_health`](https://github.com/normoes/monero_health)

### Errors
**_Note_**:

For more details on error handling, please also refer to [`monero_health`](https://github.com/normoes/monero_health)

In case of an error an `error` key is added to the responses of:
* `daemon_last_block_check`
* `daemon_status_check`
but not to `daemon_combined_status_check`.

This error key always contains the keys:
* `error`
* `message`

Example:
```
{
    "result": {
        "block_recent": false,
        "block_recent_offset": "12",
        "block_recent_offset_unit": "minutes",
        "block_timestamp": "---",
        "check_timestamp": "2020-01-07T14:53:24",
        "error": {
            "error": "-341: could not establish a connection, original error: HTTPConnectionPool(host='127.0.0.1', port=18081): Max retries exceeded with url: /json_rpc (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fe25e449cd0>: Failed to establish a new connection: [Errno 111] Connection refused'))",
            "message": "Cannot determine daemon status. Daemon: '127.0.0.1:18081'."
        },
        "hash": "---",
        "health": {
            "status": "UNKNOWN"
        }
    }
}
```
