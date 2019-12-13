# Monerod health

This is work in progress.

Monerod health is a small webserver providing a REST API.

Monerd health is supposed to provide information about the Monero daemon health.

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

TODOs (among others):
* Add functionality to send mattermost, slack notifications in case `status == "ERROR"`.
* Use proper production WSGI server, instead of Flask development server.

## Configuration

Right now, the server used is the Flask development server, not recommended for use in production.

It is configured to listen at `127.0.0.1` on port `5000`.


### Monero daemon connection
The connection to the Monero dameon can be configured using environment variables (also see `docker-compose-template.yml`):

| environment variable | default value |
|----------------------|---------------|
| `MONEROD_RPC_URL` | `"127.0.0.1"` |
| `MONEROD_RPC_PORT` | `18081` |
| `MONEROD_RPC_USER` | `""` |
| `MONEROD_RPC_PASSWORD` | `""` |

The RPC connecton is established using [`python-monerorpc`](https://github.com/monero-ecosystem/python-monerorpc).

### Last block age

`/api/v1/last_block/health` returns a `status` key.

This `status` returns whether the last block found on the daemon's blockchain is older than a pre-configured value:

| environment variable | default value |
|----------------------|---------------|
| `OFFSET` | `12` |
| `OFFSET_UNIT` | `"minutes"` |

I.e that the last block is considered out-of-date as soon as it becomes older than - in the default case - `12 [minutes]`.

In this case `status` will be `ERROR`, otherwise `status` is `OK`.

A `status` resulting in `ERROR` causes the overall `status` returned by requesting `/api/v1/health` to be `ERROR` as well.

## Result

* Requesting `/api/v1/monerod`:
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
* Requesting `/api/v1/monerod/health`:
```
{
  "result": {
    "status": "OK"
  }
}
```
* Requesting `/api/v1/last_block`.
  - The `status` (`result.last_block.health.status`) returns `ERROR`, because of the age of the last block (see timestamp values and offset):
```
{
  "result": {
    "block_recent": false,
    "block_recent_offset": 1,
    "block_recent_offset_unit": "minutes",
    "block_timestamp": "2019-12-13T12:00:12",
    "check_timestamp": "2019-12-13T12:01:27.986828",
    "hash": "eeeed694216ebe390da5bf4bb5d5e218adf1ea7f27ea37cf6910d67ad7797e23",
    "health": {
      "status": "ERROR"
    }
  }
}
```
* Requesting `/api/v1/last_block/health`.
  - Based on example above (Requesting `/api/v1/last_block`):
```
{
  "result": {
    "status": "ERROR"
  }
}
```
* Requesting `/api/v1` when the last block is considered t be out-of-date. This example uses an offset of `1 [minutes]`.
  - The overall `status` (`result.health.status`) returns `ERROR`, because of the age of the last block (`result.last_block.health.status`):
```
{
  "result": {
    "health": {
      "status": "ERROR"
    }, 
    "last_block": {
      "block_recent": false, 
      "block_recent_offset": 1, 
      "block_recent_offset_unit": "minutes", 
      "block_timestamp": "2019-12-13T11:20:43", 
      "check_timestamp": "2019-12-13T11:21:56.948074", 
      "hash": "db8b0f89d31d14e499d7af25d15b3e7ce88cd4746a71172a4342f58e1207854b", 
      "health": {
        "status": "ERROR"
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
* Requesting `/api/v1/health`.
  - Based on example above (Requesting `/api/v1`):
```
{
  "result": {
    "status": "ERROR"
  }
}
```
