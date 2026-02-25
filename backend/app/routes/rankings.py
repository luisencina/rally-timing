from flask import Blueprint, jsonify, request

from ..services.ranking_service import RankingService

rankings_bp = Blueprint("rankings", __name__)


def success(data, status=200):
    return jsonify({"success": True, "data": data}), status


@rankings_bp.route("/best-times", methods=["GET"])
def best_times():
    condition = request.args.get("condition")
    category = request.args.get("category")
    data = RankingService.get_best_times(condition=condition, category=category)
    return success(data)


@rankings_bp.route("/history/<int:pilot_id>", methods=["GET"])
def pilot_history(pilot_id):
    data = RankingService.get_pilot_history(pilot_id)
    return success(data)


@rankings_bp.route("/records", methods=["GET"])
def records():
    data = RankingService.get_records()
    return success(data)


@rankings_bp.route("/summary", methods=["GET"])
def summary():
    data = RankingService.get_summary()
    return success(data)
