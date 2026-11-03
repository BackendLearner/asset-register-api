# utils.py

from flask import jsonify
from datetime import date
import math


def error_response(message, status_code):
    return jsonify({"error": message}), status_code


def validate_purchase_cost(cost):
    if cost is None:
        return None

    if isinstance(cost, bool):
        raise ValueError

    cost = float(cost)

    if not math.isfinite(cost) or cost < 0:
        raise ValueError

    return cost


def validate_purchase_date(value):
    if value is None or value == "":
        return None

    if not isinstance(value, str):
        raise ValueError

    parsed_date = date.fromisoformat(value)

    if parsed_date.isoformat() != value:
        raise ValueError

    return parsed_date