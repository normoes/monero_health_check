from flask import Flask, jsonify
from collections import defaultdict
import logging

from monero_health.monero_health import (
    daemon_last_block_check,
    daemon_stati_check,
    daemon_combined_status_check,
    DAEMON_STATUS_UNKNOWN,
    HEALTH_KEY,
    LAST_BLOCK_KEY,
    DAEMON_KEY,
)


logging.getLogger("DaemonHealthRest").setLevel(logging.DEBUG)

app = Flask(__name__)
# Allow requests to endpoints with and without traiilng slash.
app.url_map.strict_slashes = False

API_VERSION = "v1"
API_ENDPOINT = "api"

HEALTH_ENDPOINT = HEALTH_KEY
LAST_BLOCK_ENDPOINT = LAST_BLOCK_KEY
DAEMON_ENDPOINT = DAEMON_KEY


def get_endpoint_info(func=None, params=None):
    status = DAEMON_STATUS_UNKNOWN
    response = defaultdict(dict)

    if not func:
        return response

    result = None
    if params:
        result = func(**params)
    else:
        result = func()

    if result:
        status = result.pop("status", status)
        response["result"].update(result)

    data = {HEALTH_ENDPOINT: {"status": status}}
    response["result"].update(data)
    return response


def get_status(func=None, params=None):
    status = DAEMON_STATUS_UNKNOWN
    response = defaultdict(dict)

    if not func:
        return response

    result = get_endpoint_info(func=func, params=params)
    if result and "result" in result and HEALTH_ENDPOINT in result["result"]:
        status = result["result"][HEALTH_ENDPOINT].get("status", status)

    data = {"status": status}
    response["result"].update(data)

    return response


def get_combined_endpoint_info(params=None):
    response = defaultdict(dict)

    result = None
    if params:
        result = daemon_combined_status_check(**params)
    else:
        result = daemon_combined_status_check()

    if result:
        # Move 'status' to 'health' within 'last_block'.
        if LAST_BLOCK_ENDPOINT in result:
            result_ = result[LAST_BLOCK_ENDPOINT]
            status = result_.pop("status", DAEMON_STATUS_UNKNOWN)
            data = {LAST_BLOCK_ENDPOINT: result_}
            data[LAST_BLOCK_ENDPOINT].update({HEALTH_ENDPOINT: {"status": status}})
            response["result"].update(data)

        # Move 'status' to 'health' within 'monerod'.
        if DAEMON_ENDPOINT in result:
            result_ = result[DAEMON_ENDPOINT]
            status = result_.pop("status", DAEMON_STATUS_UNKNOWN)
            data = {DAEMON_ENDPOINT: result_}
            data[DAEMON_ENDPOINT].update({HEALTH_ENDPOINT: {"status": status}})
            response["result"].update(data)

        # Move 'status' to 'health' within 'result'.
        status = DAEMON_STATUS_UNKNOWN
        host = "---"
        if "status" in result:
            status = result.pop("status", status)
        data = {HEALTH_ENDPOINT: {"status": status}}
        if "host" in result:
            host = result.pop("host", host)
        data["host"] = host
        response["result"].update(data)

    return response


def get_combined_status(params=None):
    status = DAEMON_STATUS_UNKNOWN
    response = defaultdict(dict)

    result = get_combined_endpoint_info(params=params)
    if result and "result" in result and HEALTH_ENDPOINT in result["result"]:
        status = result["result"][HEALTH_ENDPOINT].get("status", status)

    data = {"status": status}
    response["result"].update(data)

    return response


@app.route("/", methods=["GET"])
@app.route(f"/{API_ENDPOINT}/{API_VERSION}", methods=["GET"])
def index():
    """Get combined daemon status info.
    """

    # params = {"consider_p2p": True}
    params = {}

    response = get_combined_endpoint_info(params=params)

    return jsonify(response)


# Combines all health endpoints
# and shows overall status.
@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{HEALTH_ENDPOINT}", methods=["GET"])
def overall_health():
    """Get combined daemon status.
    """

    # params = {"consider_p2p": True}
    params = {}

    response = get_combined_status(params=params)

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}", methods=["GET"])
def daemon():
    """Get daemon info.
    """

    # params = {"consider_p2p": True}
    params = {}

    response = get_endpoint_info(func=daemon_stati_check, params=params)

    return jsonify(response)


@app.route(
    f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}/{HEALTH_ENDPOINT}",
    methods=["GET"],
)
def daemon_health():
    """Get daemon status.
    """

    # params = {"consider_p2p": True}
    params = {}

    response = get_status(func=daemon_stati_check, params=params)
    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}", methods=["GET"])
def last_block():
    """Get daemon's last block info.
    """

    response = get_endpoint_info(func=daemon_last_block_check)
    return jsonify(response)


@app.route(
    f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}/{HEALTH_ENDPOINT}",
    methods=["GET"],
)
def last_block_health():
    """Get dameon's last block status.
    """

    response = get_status(func=daemon_last_block_check)
    return jsonify(response)


if __name__ == "__main__":
    # Add 'nosec' comment to make bandit ignore [B104:hardcoded_bind_all_interfaces], [B201:flask_debug_true].
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)  # nosec
