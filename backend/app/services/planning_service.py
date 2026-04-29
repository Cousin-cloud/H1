from datetime import datetime, timedelta
import pandas as pd

REQUIRED_COLUMNS = [
    "division", "plant_type", "project_name", "client", "forecast_type", "operation",
    "required_man_hours", "production_start_date", "production_end_date"
]

ALIASES = {
    "division": ["division", "business_division"],
    "plant_type": ["plant", "plant_type", "plant type"],
    "project_name": ["project", "project_name"],
    "client": ["client", "customer"],
    "forecast_type": ["forecast", "forecast_type"],
    "operation": ["operation", "process"],
    "required_man_hours": ["required_man_hours", "hours", "man_hours"],
    "production_start_date": ["production_start_date", "start_date"],
    "production_end_date": ["production_end_date", "end_date"],
}


def normalize_columns(df: pd.DataFrame):
    mapping = {}
    cols = {str(c).strip().lower(): c for c in df.columns}
    for canonical, aliases in ALIASES.items():
        match = next((cols[a.lower()] for a in aliases if a.lower() in cols), None)
        if match:
            mapping[match] = canonical
    return df.rename(columns=mapping)


def parse_file(file_bytes: bytes, filename: str):
    if filename.lower().endswith('.csv'):
        return pd.read_csv(pd.io.common.BytesIO(file_bytes))
    return pd.read_excel(pd.io.common.BytesIO(file_bytes))


def validate_rows(df: pd.DataFrame):
    df = normalize_columns(df)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    valid_rows, errors = [], []
    for idx, row in df.iterrows():
        try:
            start = pd.to_datetime(row["production_start_date"], errors="raise")
            end = pd.to_datetime(row["production_end_date"], errors="raise")
            if end < start:
                raise ValueError("end date before start date")
            days = (end - start).days + 1
            if days <= 0:
                raise ValueError("invalid date span")
            daily_hours = float(row["required_man_hours"]) / days
            for day_offset in range(days):
                d = start + timedelta(days=day_offset)
                valid_rows.append({
                    "division": str(row["division"]).strip(),
                    "plant_type": str(row["plant_type"]).strip(),
                    "project_name": str(row["project_name"]).strip(),
                    "client": str(row["client"]).strip(),
                    "forecast_type": str(row["forecast_type"]).strip(),
                    "operation": str(row["operation"]).strip(),
                    "required_man_hours": round(daily_hours, 2),
                    "work_date": d.strftime("%Y-%m-%d"),
                })
        except Exception as exc:
            errors.append({"row_number": int(idx) + 2, "reason": str(exc), "raw_data": row.fillna('').to_dict()})
    return valid_rows, errors


def build_planning(demand_rows, capacity_rows, scenario):
    accepted = {"confirmed": ["Confirmed"], "confirmed_probable": ["Confirmed", "Probable"], "all": ["Confirmed", "Probable", "Potential"]}[scenario]
    d = pd.DataFrame([r for r in demand_rows if r["forecast_type"] in accepted])
    if d.empty:
        return []
    d["month"] = pd.to_datetime(d["work_date"]).dt.strftime("%Y-%m")
    demand = d.groupby(["month", "plant_type", "operation", "division"], as_index=False)["required_man_hours"].sum()

    c = pd.DataFrame(capacity_rows)
    c["daily_capacity"] = c["workers_per_shift"] * c["hours_per_shift"]
    cap = c.groupby(["plant_type", "operation"], as_index=False).agg({"daily_capacity": "sum", "working_days_per_month": "max"})
    cap["monthly_capacity"] = cap["daily_capacity"] * cap["working_days_per_month"]
    cap["stretch_capacity"] = cap["monthly_capacity"] * 1.2

    merged = demand.merge(cap, on=["plant_type", "operation"], how="left")
    merged["monthly_capacity"] = merged["monthly_capacity"].fillna(0)
    merged["stretch_capacity"] = merged["stretch_capacity"].fillna(0)
    merged["surplus_shortfall"] = merged["monthly_capacity"] - merged["required_man_hours"]
    merged["status"] = merged.apply(lambda x: "red" if x["required_man_hours"] > x["stretch_capacity"] else ("amber" if x["required_man_hours"] > x["monthly_capacity"] else "green"), axis=1)
    return merged.to_dict("records")
