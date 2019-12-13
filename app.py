from flask import Flask, jsonify
from collections import defaultdict
import logging

from monero_health import (
    daemon_last_block_check,
    daemon_status_check,
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
DAEMON_STATUS_OK = "OK"
DAEMON_STATUS_ERROR = "ERROR"


@app.route(f"/{API_ENDPOINT}/{API_VERSION}", methods=["GET"])
def index():
    response = defaultdict(dict)

    last_block_status = False
    daemon_status = False

    result = daemon_last_block_check()
    if result:
        last_block_status = True if result.get("block_recent", False) else False
        data = dict({LAST_BLOCK_ENDPOINT: result})
        last_block_status = True if result.get("block_recent", False) else False
        data[LAST_BLOCK_ENDPOINT].update({HEALTH_ENDPOINT: {"status": DAEMON_STATUS_OK if all((last_block_status,)) else DAEMON_STATUS_ERROR}})
        response["result"].update(data)

    result = daemon_status_check()
    if result:
        daemon_status = True if result.get("status", None) == DAEMON_STATUS_OK else False
        data = dict({DAEMON_ENDPOINT: {"version": result.get("version", "---")}})
        data[DAEMON_ENDPOINT].update({HEALTH_ENDPOINT: {"status": result.get("status", "---")}})
        response["result"].update(data)

    data = {HEALTH_ENDPOINT: {"status": DAEMON_STATUS_OK if all((last_block_status, daemon_status)) else DAEMON_STATUS_ERROR}}


    response["result"].update(data)

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}", methods=["GET"])
def daemon():
    response = defaultdict(dict)

    daemon_status = False

    result = daemon_status_check()
    if result:
        daemon_status = True if result.get("status", None) == DAEMON_STATUS_OK else False
        response["result"].update({"version": result.get("version", "---")})

    data = {HEALTH_ENDPOINT: {"status": DAEMON_STATUS_OK if all((daemon_status,)) else DAEMON_STATUS_ERROR}}
    response["result"].update(data)

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{DAEMON_ENDPOINT}/{HEALTH_ENDPOINT}", methods=["GET"])
def daemon_health():
    response = defaultdict(dict)

    daemon_status = False

    result = daemon_status_check()
    if result:
        daemon_status = True if result.get("status", None) == DAEMON_STATUS_OK else False

    response["result"].update({"status": DAEMON_STATUS_OK if all((daemon_status,)) else DAEMON_STATUS_ERROR})

    return jsonify(response)


# Combines all health endpoints
# and shows overall status.
@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{HEALTH_ENDPOINT}", methods=["GET"])
def overall_health():
    response = defaultdict(dict)

    last_block_status = False
    daemon_status = False

    result = daemon_last_block_check()
    if result:
        last_block_status = True if result.get("block_recent", False) else False

    result = daemon_status_check()
    if result:
        daemon_status = True if result.get("status", None) == DAEMON_STATUS_OK else False

    response["result"] = {"status": DAEMON_STATUS_OK if all((last_block_status, daemon_status)) else DAEMON_STATUS_ERROR}

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}", methods=["GET"])
def last_block():
    response = defaultdict(dict)
    
    last_block_status = False

    result = daemon_last_block_check()
    if result:
        last_block_status = True if result.get("block_recent", False) else False
        response["result"].update(result)
    
    data = {HEALTH_ENDPOINT: {"status": DAEMON_STATUS_OK if all((last_block_status,)) else DAEMON_STATUS_ERROR}}
    response["result"].update(data)

    return jsonify(response)


@app.route(f"/{API_ENDPOINT}/{API_VERSION}/{LAST_BLOCK_ENDPOINT}/{HEALTH_ENDPOINT}", methods=["GET"])
def last_block_healh():
    response = defaultdict(dict)
    
    last_block_status = False

    result = daemon_last_block_check()
    if result:
        last_block_status = True if result.get("block_recent", False) else False
    
    response["result"].update({"status": DAEMON_STATUS_OK if all((last_block_status,)) else DAEMON_STATUS_ERROR})

    return jsonify(response)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
