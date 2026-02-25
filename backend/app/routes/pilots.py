from flask import Blueprint, jsonify, request

from ..models import db, Pilot, SyncLog

pilots_bp = Blueprint("pilots", __name__)


def success(data, status=200):
    return jsonify({"success": True, "data": data}), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def log_sync(table, record_id, action):
    entry = SyncLog(table_name=table, record_id=record_id, action=action)
    db.session.add(entry)


@pilots_bp.route("", methods=["GET"])
def list_pilots():
    query = Pilot.query.filter_by(is_active=1)

    search = request.args.get("search")
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                Pilot.first_name.ilike(pattern),
                Pilot.last_name.ilike(pattern),
                Pilot.nickname.ilike(pattern),
            )
        )

    pilots = query.order_by(Pilot.last_name).all()
    return success([p.to_dict() for p in pilots])


@pilots_bp.route("/<int:pilot_id>", methods=["GET"])
def get_pilot(pilot_id):
    pilot = Pilot.query.get(pilot_id)
    if not pilot or not pilot.is_active:
        return error("Piloto no encontrado", 404)
    return success(pilot.to_dict())


@pilots_bp.route("", methods=["POST"])
def create_pilot():
    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    if not first_name or not last_name:
        return error("Nombre y apellido son requeridos")

    pilot = Pilot(
        first_name=first_name,
        last_name=last_name,
        nickname=data.get("nickname", "").strip() or None,
        phone=data.get("phone", "").strip() or None,
        email=data.get("email", "").strip() or None,
        license_number=data.get("license_number", "").strip() or None,
        notes=data.get("notes", "").strip() or None,
    )
    db.session.add(pilot)
    db.session.flush()
    log_sync("pilots", pilot.id, "create")
    db.session.commit()
    return success(pilot.to_dict(), 201)


@pilots_bp.route("/<int:pilot_id>", methods=["PUT"])
def update_pilot(pilot_id):
    pilot = Pilot.query.get(pilot_id)
    if not pilot or not pilot.is_active:
        return error("Piloto no encontrado", 404)

    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    if "first_name" in data:
        val = data["first_name"].strip()
        if not val:
            return error("Nombre es requerido")
        pilot.first_name = val
    if "last_name" in data:
        val = data["last_name"].strip()
        if not val:
            return error("Apellido es requerido")
        pilot.last_name = val

    for field in ("nickname", "phone", "email", "license_number", "notes"):
        if field in data:
            setattr(pilot, field, data[field].strip() or None)

    log_sync("pilots", pilot.id, "update")
    db.session.commit()
    return success(pilot.to_dict())


@pilots_bp.route("/<int:pilot_id>", methods=["DELETE"])
def delete_pilot(pilot_id):
    pilot = Pilot.query.get(pilot_id)
    if not pilot or not pilot.is_active:
        return error("Piloto no encontrado", 404)

    pilot.is_active = 0
    log_sync("pilots", pilot.id, "delete")
    db.session.commit()
    return success({"message": "Piloto desactivado"})
