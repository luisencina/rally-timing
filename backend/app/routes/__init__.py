from flask import Flask, jsonify

from .pilots import pilots_bp
from .cars import cars_bp
from .runs import runs_bp
from .rankings import rankings_bp


def register_routes(app: Flask):
    app.register_blueprint(pilots_bp, url_prefix="/api/pilots")
    app.register_blueprint(cars_bp, url_prefix="/api/cars")
    app.register_blueprint(runs_bp, url_prefix="/api/runs")
    app.register_blueprint(rankings_bp, url_prefix="/api/rankings")

    @app.route("/api/health")
    def health():
        return jsonify({"success": True, "data": {"status": "ok"}})
