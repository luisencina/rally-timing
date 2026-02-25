from flask import Blueprint, jsonify, request

from ..models import db, Car, Pilot, SyncLog

cars_bp = Blueprint("cars", __name__)


def success(data, status=200):
    return jsonify({"success": True, "data": data}), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def log_sync(table, record_id, action):
    entry = SyncLog(table_name=table, record_id=record_id, action=action)
    db.session.add(entry)


@cars_bp.route("", methods=["GET"])
def list_cars():
    query = Car.query.filter_by(is_active=1)

    pilot_id = request.args.get("pilot_id")
    if pilot_id:
        query = query.filter_by(pilot_id=int(pilot_id))

    category = request.args.get("category")
    if category:
        query = query.filter_by(category=category)

    cars = query.order_by(Car.brand, Car.model).all()
    result = []
    for car in cars:
        d = car.to_dict()
        if car.pilot:
            d["pilot_name"] = f"{car.pilot.first_name} {car.pilot.last_name}"
        else:
            d["pilot_name"] = None
        result.append(d)
    return success(result)


@cars_bp.route("/<int:car_id>", methods=["GET"])
def get_car(car_id):
    car = Car.query.get(car_id)
    if not car or not car.is_active:
        return error("Auto no encontrado", 404)
    d = car.to_dict()
    if car.pilot:
        d["pilot_name"] = f"{car.pilot.first_name} {car.pilot.last_name}"
    return success(d)


@cars_bp.route("", methods=["POST"])
def create_car():
    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    brand = data.get("brand", "").strip()
    model = data.get("model", "").strip()
    category = data.get("category", "").strip()
    if not brand or not model or not category:
        return error("Marca, modelo y categoria son requeridos")

    pilot_id = data.get("pilot_id")
    if pilot_id:
        pilot = Pilot.query.get(pilot_id)
        if not pilot or not pilot.is_active:
            return error("Piloto no encontrado", 404)

    car = Car(
        brand=brand,
        model=model,
        year=data.get("year"),
        plate_number=data.get("plate_number", "").strip() or None,
        category=category,
        pilot_id=pilot_id,
        notes=data.get("notes", "").strip() or None,
    )
    db.session.add(car)
    db.session.flush()
    log_sync("cars", car.id, "create")
    db.session.commit()
    return success(car.to_dict(), 201)


@cars_bp.route("/<int:car_id>", methods=["PUT"])
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car or not car.is_active:
        return error("Auto no encontrado", 404)

    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    if "brand" in data:
        val = data["brand"].strip()
        if not val:
            return error("Marca es requerida")
        car.brand = val
    if "model" in data:
        val = data["model"].strip()
        if not val:
            return error("Modelo es requerido")
        car.model = val
    if "category" in data:
        val = data["category"].strip()
        if not val:
            return error("Categoria es requerida")
        car.category = val

    if "year" in data:
        car.year = data["year"]
    if "pilot_id" in data:
        if data["pilot_id"]:
            pilot = Pilot.query.get(data["pilot_id"])
            if not pilot or not pilot.is_active:
                return error("Piloto no encontrado", 404)
        car.pilot_id = data["pilot_id"]

    for field in ("plate_number", "notes"):
        if field in data:
            setattr(car, field, data[field].strip() or None)

    log_sync("cars", car.id, "update")
    db.session.commit()
    return success(car.to_dict())


@cars_bp.route("/<int:car_id>", methods=["DELETE"])
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car or not car.is_active:
        return error("Auto no encontrado", 404)

    car.is_active = 0
    log_sync("cars", car.id, "delete")
    db.session.commit()
    return success({"message": "Auto desactivado"})
