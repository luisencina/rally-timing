import pandas as pd

from ..models import db, Run, Pilot, Car


class RankingService:

    @staticmethod
    def _get_valid_runs_df(condition=None, category=None):
        """Get all valid runs as a DataFrame, including penalty-adjusted times."""
        query = (
            Run.query
            .join(Pilot, Run.pilot_id == Pilot.id)
            .join(Car, Run.car_id == Car.id)
            .filter(Run.is_valid == 1)
            .filter(Pilot.is_active == 1)
        )

        if condition:
            query = query.filter(Run.track_condition == condition)
        if category:
            query = query.filter(Run.car_category == category)

        runs = query.all()
        if not runs:
            return None

        rows = []
        for r in runs:
            rows.append({
                "id": r.id,
                "pilot_id": r.pilot_id,
                "car_id": r.car_id,
                "run_date": r.run_date,
                "total_time_ms": r.total_time_ms,
                "final_time_ms": r.final_time_ms,
                "penalty_total_ms": r.penalty_total_ms,
                "track_condition": r.track_condition,
                "car_category": r.car_category,
                "source": r.source,
                "first_name": r.pilot.first_name,
                "last_name": r.pilot.last_name,
                "nickname": r.pilot.nickname,
                "car_brand": r.car.brand,
                "car_model": r.car.model,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def get_best_times(condition=None, category=None):
        """Best final time (with penalties) per pilot, sorted ascending."""
        df = RankingService._get_valid_runs_df(condition, category)
        if df is None:
            return []

        # Get best final time per pilot
        idx = df.groupby("pilot_id")["final_time_ms"].idxmin()
        best = df.loc[idx].sort_values("final_time_ms").reset_index(drop=True)

        result = []
        for pos, (_, row) in enumerate(best.iterrows(), 1):
            entry = {
                "position": pos,
                "pilot_id": int(row["pilot_id"]),
                "pilot_name": f"{row['first_name']} {row['last_name']}",
                "nickname": row["nickname"],
                "car_name": f"{row['car_brand']} {row['car_model']}",
                "best_time_ms": int(row["final_time_ms"]),
                "total_time_ms": int(row["total_time_ms"]),
                "penalty_total_ms": int(row["penalty_total_ms"]),
                "run_date": row["run_date"],
                "track_condition": row["track_condition"],
                "car_category": row["car_category"],
            }
            result.append(entry)
        return result

    @staticmethod
    def get_pilot_history(pilot_id):
        """All valid runs for a specific pilot, sorted by date."""
        df = RankingService._get_valid_runs_df()
        if df is None:
            return []

        pilot_df = df[df["pilot_id"] == pilot_id].sort_values("run_date")
        if pilot_df.empty:
            return []

        return [
            {
                "run_id": int(row["id"]),
                "run_date": row["run_date"],
                "total_time_ms": int(row["total_time_ms"]),
                "final_time_ms": int(row["final_time_ms"]),
                "penalty_total_ms": int(row["penalty_total_ms"]),
                "car_name": f"{row['car_brand']} {row['car_model']}",
                "track_condition": row["track_condition"],
                "car_category": row["car_category"],
            }
            for _, row in pilot_df.iterrows()
        ]

    @staticmethod
    def get_records():
        """Track records: overall, by category, by condition (using final time)."""
        df = RankingService._get_valid_runs_df()
        if df is None:
            return {"overall": None, "by_category": [], "by_condition": []}

        def format_record(row):
            return {
                "pilot_name": f"{row['first_name']} {row['last_name']}",
                "best_time_ms": int(row["final_time_ms"]),
                "total_time_ms": int(row["total_time_ms"]),
                "penalty_total_ms": int(row["penalty_total_ms"]),
                "car_name": f"{row['car_brand']} {row['car_model']}",
                "run_date": row["run_date"],
                "track_condition": row["track_condition"],
                "car_category": row["car_category"],
            }

        # Overall record
        overall_idx = df["final_time_ms"].idxmin()
        overall = format_record(df.loc[overall_idx])

        # By category
        by_category = []
        for cat, group in df.groupby("car_category"):
            best_idx = group["final_time_ms"].idxmin()
            rec = format_record(group.loc[best_idx])
            rec["category"] = cat
            by_category.append(rec)

        # By condition
        by_condition = []
        for cond, group in df.groupby("track_condition"):
            best_idx = group["final_time_ms"].idxmin()
            rec = format_record(group.loc[best_idx])
            rec["condition"] = cond
            by_condition.append(rec)

        return {
            "overall": overall,
            "by_category": by_category,
            "by_condition": by_condition,
        }

    @staticmethod
    def get_summary():
        """Dashboard summary stats."""
        total_pilots = Pilot.query.filter_by(is_active=1).count()
        total_cars = Car.query.filter_by(is_active=1).count()
        total_runs = Run.query.filter_by(is_valid=1).count()

        # Best record (using final_time_ms)
        valid_runs = Run.query.filter_by(is_valid=1).all()
        record = None
        if valid_runs:
            best_run = min(valid_runs, key=lambda r: r.final_time_ms)
            pilot = Pilot.query.get(best_run.pilot_id)
            car = Car.query.get(best_run.car_id)
            record = {
                "pilot_name": f"{pilot.first_name} {pilot.last_name}" if pilot else "?",
                "car_name": f"{car.brand} {car.model}" if car else "?",
                "best_time_ms": best_run.final_time_ms,
                "run_date": best_run.run_date,
            }

        # Latest 5 runs
        latest = (
            Run.query.filter_by(is_valid=1)
            .order_by(Run.created_at.desc())
            .limit(5)
            .all()
        )
        latest_runs = []
        for run in latest:
            d = run.to_dict()
            if run.pilot:
                d["pilot_name"] = f"{run.pilot.first_name} {run.pilot.last_name}"
            if run.car:
                d["car_name"] = f"{run.car.brand} {run.car.model}"
            latest_runs.append(d)

        return {
            "total_pilots": total_pilots,
            "total_cars": total_cars,
            "total_runs": total_runs,
            "record": record,
            "latest_runs": latest_runs,
        }
