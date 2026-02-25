from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class Pilot(db.Model):
    __tablename__ = "pilots"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=True)
    phone = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    license_number = db.Column(db.String, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    cars = db.relationship("Car", backref="pilot", lazy=True)
    runs = db.relationship("Run", backref="pilot", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "phone": self.phone,
            "email": self.email,
            "license_number": self.license_number,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Car(db.Model):
    __tablename__ = "cars"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    brand = db.Column(db.String, nullable=False)
    model = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    plate_number = db.Column(db.String, nullable=True)
    category = db.Column(db.String, nullable=False)
    pilot_id = db.Column(db.Integer, db.ForeignKey("pilots.id"), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    runs = db.relationship("Run", backref="car", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "brand": self.brand,
            "model": self.model,
            "year": self.year,
            "plate_number": self.plate_number,
            "category": self.category,
            "pilot_id": self.pilot_id,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


VALID_TRACK_CONDITIONS = ("dry", "wet", "humid")
VALID_SOURCES = ("manual", "stopwatch")


class Run(db.Model):
    __tablename__ = "runs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pilot_id = db.Column(db.Integer, db.ForeignKey("pilots.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    run_date = db.Column(db.String, nullable=False)
    total_time_ms = db.Column(db.Integer, nullable=False)
    track_condition = db.Column(db.String, nullable=False)
    car_category = db.Column(db.String, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    is_valid = db.Column(db.Integer, default=1)
    source = db.Column(db.String, default="manual")
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    penalties = db.relationship("Penalty", backref="run", lazy=True)

    @property
    def penalty_total_ms(self):
        return sum(p.time_ms for p in self.penalties)

    @property
    def final_time_ms(self):
        return self.total_time_ms + self.penalty_total_ms

    def to_dict(self):
        penalty_ms = self.penalty_total_ms
        return {
            "id": self.id,
            "pilot_id": self.pilot_id,
            "car_id": self.car_id,
            "run_date": self.run_date,
            "total_time_ms": self.total_time_ms,
            "penalty_total_ms": penalty_ms,
            "final_time_ms": self.total_time_ms + penalty_ms,
            "penalties": [p.to_dict() for p in self.penalties],
            "track_condition": self.track_condition,
            "car_category": self.car_category,
            "notes": self.notes,
            "is_valid": self.is_valid,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Penalty(db.Model):
    __tablename__ = "penalties"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_id = db.Column(db.Integer, db.ForeignKey("runs.id"), nullable=False)
    time_ms = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "run_id": self.run_id,
            "time_ms": self.time_ms,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SyncLog(db.Model):
    __tablename__ = "sync_log"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String, nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String, nullable=False)
    synced = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=utcnow)
