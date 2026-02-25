from flask import Blueprint, jsonify, request

from ..models import db, Category, SyncLog

categories_bp = Blueprint("categories", __name__)


def success(data, status=200):
    return jsonify({"success": True, "data": data}), status


def error(message, status=400):
    return jsonify({"success": False, "error": message}), status


def log_sync(table, record_id, action):
    entry = SyncLog(table_name=table, record_id=record_id, action=action)
    db.session.add(entry)


@categories_bp.route("", methods=["GET"])
def list_categories():
    query = Category.query.filter_by(is_active=1)

    search = request.args.get("search")
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    categories = query.order_by(Category.name).all()
    return success([c.to_dict() for c in categories])


@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category or not category.is_active:
        return error("Categoria no encontrada", 404)
    return success(category.to_dict())


@categories_bp.route("", methods=["POST"])
def create_category():
    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    name = data.get("name", "").strip()
    if not name:
        return error("Nombre de categoria es requerido")

    existing = Category.query.filter(
        db.func.lower(Category.name) == name.lower(),
        Category.is_active == 1,
    ).first()
    if existing:
        return error(f"Ya existe una categoria con el nombre '{name}'")

    category = Category(
        name=name,
        description=data.get("description", "").strip() or None,
    )
    db.session.add(category)
    db.session.flush()
    log_sync("categories", category.id, "create")
    db.session.commit()
    return success(category.to_dict(), 201)


@categories_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category or not category.is_active:
        return error("Categoria no encontrada", 404)

    data = request.get_json()
    if not data:
        return error("Datos requeridos")

    if "name" in data:
        name = data["name"].strip()
        if not name:
            return error("Nombre es requerido")
        existing = Category.query.filter(
            db.func.lower(Category.name) == name.lower(),
            Category.is_active == 1,
            Category.id != category_id,
        ).first()
        if existing:
            return error(f"Ya existe una categoria con el nombre '{name}'")
        category.name = name

    if "description" in data:
        category.description = data["description"].strip() or None

    log_sync("categories", category.id, "update")
    db.session.commit()
    return success(category.to_dict())


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category or not category.is_active:
        return error("Categoria no encontrada", 404)

    category.is_active = 0
    log_sync("categories", category.id, "delete")
    db.session.commit()
    return success({"message": "Categoria desactivada"})
