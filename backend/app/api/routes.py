from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.security import require_roles, get_current_user
from app.services.planning_service import parse_file, validate_rows, build_planning
from app.db.supabase_client import supabase
from datetime import datetime

router = APIRouter()

@router.post('/upload/preview')
async def upload_preview(file: UploadFile = File(...), user=Depends(require_roles('admin','planner'))):
    content = await file.read()
    df = parse_file(content, file.filename)
    valid_rows, errors = validate_rows(df)
    return {"valid_count": len(valid_rows), "error_count": len(errors), "sample_valid": valid_rows[:20], "errors": errors[:50]}

@router.post('/upload/confirm')
async def upload_confirm(file: UploadFile = File(...), user=Depends(require_roles('admin','planner'))):
    content = await file.read()
    df = parse_file(content, file.filename)
    valid_rows, errors = validate_rows(df)
    log = supabase.table("upload_logs").insert({"filename": file.filename, "uploaded_by": user["id"], "valid_count": len(valid_rows), "error_count": len(errors)}).execute().data[0]
    if valid_rows:
        for r in valid_rows:
            r["upload_log_id"] = log["id"]
        supabase.table("demand_records").insert(valid_rows).execute()
    if errors:
        for e in errors:
            e["upload_log_id"] = log["id"]
        supabase.table("upload_error_logs").insert(errors).execute()
    return {"message": "Upload processed", "upload_log_id": log["id"], "valid_count": len(valid_rows), "error_count": len(errors)}

@router.get('/capacity')
def list_capacity(user=Depends(get_current_user)):
    return supabase.table("capacity_config").select("*").order("plant_type").execute().data

@router.post('/capacity')
def upsert_capacity(payload: dict, user=Depends(require_roles('admin'))):
    return supabase.table("capacity_config").upsert(payload).execute().data

@router.get('/planning')
def planning(scenario: str = "confirmed", user=Depends(get_current_user)):
    if scenario not in ["confirmed", "confirmed_probable", "all"]:
        raise HTTPException(400, "invalid scenario")
    demands = supabase.table("demand_records").select("*").execute().data
    caps = supabase.table("capacity_config").select("*").execute().data
    return build_planning(demands, caps, scenario)
