from flask import Flask, jsonify
from collections import defaultdict
import logging

from monero_health import (
    daemon_last_block_check,
    daemon_status_check,
    DAEMON_STATUS_OK,
    DAEMON_STATUS_ERROR,
)


logging.getLogger("DaemonHealth").setLevel(logging.DEBUG)

app = Flask(__name__)
# Allow requests to endpoints with and without traiilng slash.
# app.url_map.strict_slashes = False

API_VERSION = "v1"
API_ENDPOINT = "api"
HEALTH_ENDPOINT = "health"
LAST_BLOCK_ENDPOINT = "last_block"
DAEMON_ENDPOINT = "monerod"


def get_endpoint_info(func=None):
    status = DAEMON_STATUS_ERROR
    response = defaultdict(dict)
    
    if not func:
        return response

    result = func()
    if result:
        status = result.pop("status", status)
        response["result"].update(result)
    
    data = {HEALTH_ENDPOINT: {"status": status}}
    response["result"].update(data)
    return response


def get_status(func=None):
    status = DAEMON_STATUS_ERROR
    response = defaultdict(dict)
    
    if not func:
        return response

    result = get_endpoint_info(func)
    if result and "result" in result and HEALTH_ENDPOINT in result["result"]:
        status = result["result"][HEALTH_ENDPOINT].get("status", status) 
    
    data = {"status": status}
    response["result"].update(data)

    return response


def get_combined_endpoint_info():
    response = defaultdict(dict)

    last_block_status = False
    daemon_status = False

    result = get_endpoint_info(daemon_last_block_check)
    if result and "result" in result:
        result_ = result["result"]
        status = DAEMON_STATUS_ERROR 
        if HEALTH_ENDPOINT in result_:
            status = result_[HEALTH_ENDPOINT].pop("status", DAEMON_STATUS_ERROR)
            del result_[HEALTH_ENDPOINT]
        # last_block_status = result_.get("block_recent", last_block_status)
        last_block_status  = True if status == DAEMON_STATUS_OK else False
        data = {LAST_BLOCK_ENDPOINT: result_}
        data[LAST_BLOCK_ENDPOINT].update({HEALTH_ENDPOINT: {"status": status}})
        response["result"].update(data)

    result = get_endpoint_info(daemon_status_check)
    if result and "result" in result:
        result_ = result["result"]
        status = DAEMON_STATUS_ERROR 
        if HEALTH_ENDPOINT in result_:
            status = result_[HEALTH_ENDPOINT].pop("status", DAEMON_STATUS_ERROR)
            del result_[HEALTH_ENDPOINT]
        daemon_status = True if status == DAEMON_STATUS_OK else False
        data = {DAEMON_ENDPOINT: result_}
        data[DAEMON_ENDPOINT].update({HEALTH_ENDPOINT: {"status": status}})
        response["result"].update(data)

    data = {HEALTH_ENDPOINT: {"status": DAEMON_STATUS_OK if all((last_block_status, daemon_status)) else DAEMON_STATUS_ERROR}}

    response["result"].update(data)

    return response


def get_combined_status():
    status = DAEMON_STATUS_ERROR
    response = defaultdict(dict)
    
    result = get_combined_endpoint_info()
    print(result)
    if result and "result" in result and HEALTH_ENDPOINT in result["result"]:
        status = result["result"][HEALTH_ENDPOINT].get("status", status) 
    
    data = {"status": status}
    response["result"].update(data)

    return response


@app.route(f"/{API_ENDPOINT}/{API_VERSION}", methods=["GET"])
def index():
    """Get combined daemon status info.
    """

    response = get_combined_endpoint_info()

    return jsonify(response)


# Combines all health endpoints
# and shows overall status.
@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{HEALTH_ENDPOINT}", methods=["GET"])
def overall_health():
    """Get combined daemon status.
    """

    response = get_combined_status()

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}", methods=["GET"])
def daemon():
    """Get daemon info.
    """

    response = get_endpoint_info(func=daemon_status_check)

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}/{HEALTH_ENDPOINT}", methods=["GET"])
def daemon_health():
    """Get daemon status.
    """

    response = get_status(func=daemon_status_check)
    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}", methods=["GET"])
def last_block():
    """Get daemon's last block info.
    """

    response = get_endpoint_info(func=daemon_last_block_check)
    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}/{HEALTH_ENDPOINT}", methods=["GET"])
def last_block_health():
    """Get dameon's last block status.
    """

    response = get_status(func=daemon_last_block_check)
    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
