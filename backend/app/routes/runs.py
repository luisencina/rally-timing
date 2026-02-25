from flask import Blueprint, jsonify, request

from ..models import (
    db,
    Run,
    Pilot,
    Car,
    SyncLog,
    VALID_TRACK_CONDITIONS,
    VALID_SOURCES,
)

runs_bp = Blueprint("runs", __name__)


def success(data, status=200):
    return jsonify({"success": True, "data": data}), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def log_sync(table, record_id, action):
    entry = SyncLog(table_name=table, record_id=record_id, action=action)
    db.session.add(entry)


def enrich_run(run):
    """Add pilot and car names to a run dict."""
    d = run.to_dict()
    if run.pilot:
        d["pilot_name"] = f"{run.pilot.first_name} {run.pilot.last_name}"
    if run.car:
        d["car_name"] = f"{run.car.brand} {run.car.model}"
    return d


@runs_bp.route("", methods=["GET"])
def list_runs():
    query = Run.query.filter_by(is_valid=1)

    pilot_id = request.args.get("pilot_id")
    if pilot_id:
        query = query.filter_by(pilot_id=int(pilot_id))

    date = request.args.get("date")
    if date:
        query = query.filter_by(run_date=date)

    condition = request.args.get("condition")
    if condition:
        query = query.filter_by(track_condition=condition)

    category = request.args.get("category")
    if category:
        query = query.filter_by(car_category=category)

    runs = query.order_by(Run.run_date.desc(), Run.created_at.desc()).all()
    return success([enrich_run(r) for r in runs])


@runs_bp.route("/<int:run_id>", methods=["GET"])
def get_run(run_id):
    run = Run.query.get(run_id)
    if not run or not run.is_valid:
        return error("Pasada no encontrada", 404)
    return success(enrich_run(run))


@runs_bp.route("", methods=["POST"])
def create_run():
    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    # Validate required fields
    pilot_id = data.get("pilot_id")
    car_id = data.get("car_id")
    run_date = data.get("run_date", "").strip()
    total_time_ms = data.get("total_time_ms")
    track_condition = data.get("track_condition", "").strip()

    if not all([pilot_id, car_id, run_date, total_time_ms is not None, track_condition]):
        return error("pilot_id, car_id, run_date, total_time_ms y track_condition son requeridos")

    if track_condition not in VALID_TRACK_CONDITIONS:
        return error(f"Condicion invalida. Opciones: {', '.join(VALID_TRACK_CONDITIONS)}")

    if not isinstance(total_time_ms, int) or total_time_ms <= 0:
        return error("total_time_ms debe ser un entero positivo (milisegundos)")

    source = data.get("source", "manual").strip()
    if source not in VALID_SOURCES:
        return error(f"Source invalido. Opciones: {', '.join(VALID_SOURCES)}")

    # Validate pilot exists
    pilot = Pilot.query.get(pilot_id)
    if not pilot or not pilot.is_active:
        return error("Piloto no encontrado", 404)

    # Validate car exists
    car = Car.query.get(car_id)
    if not car or not car.is_active:
        return error("Auto no encontrado", 404)

    run = Run(
        pilot_id=pilot_id,
        car_id=car_id,
        run_date=run_date,
        total_time_ms=total_time_ms,
        track_condition=track_condition,
        car_category=car.category,
        notes=data.get("notes", "").strip() or None,
        source=source,
    )
    db.session.add(run)
    db.session.flush()
    log_sync("runs", run.id, "create")
    db.session.commit()
    return success(enrich_run(run), 201)


@runs_bp.route("/<int:run_id>", methods=["PUT"])
def update_run(run_id):
    run = Run.query.get(run_id)
    if not run or not run.is_valid:
        return error("Pasada no encontrada", 404)

    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    if "total_time_ms" in data:
        if not isinstance(data["total_time_ms"], int) or data["total_time_ms"] <= 0:
            return error("total_time_ms debe ser un entero positivo")
        run.total_time_ms = data["total_time_ms"]

    if "track_condition" in data:
        if data["track_condition"] not in VALID_TRACK_CONDITIONS:
            return error(f"Condicion invalida. Opciones: {', '.join(VALID_TRACK_CONDITIONS)}")
        run.track_condition = data["track_condition"]

    if "notes" in data:
        run.notes = data["notes"].strip() or None

    if "run_date" in data:
        run.run_date = data["run_date"].strip()

    log_sync("runs", run.id, "update")
    db.session.commit()
    return success(enrich_run(run))


@runs_bp.route("/<int:run_id>", methods=["DELETE"])
def delete_run(run_id):
    run = Run.query.get(run_id)
    if not run or not run.is_valid:
        return error("Pasada no encontrada", 404)

    run.is_valid = 0
    log_sync("runs", run.id, "delete")
    db.session.commit()
    return success({"message": "Pasada invalidada"})
