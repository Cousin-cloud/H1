from fastapi import Header, HTTPException, Depends
import jwt
from app.core.config import settings
from app.db.supabase_client import supabase


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Unauthorized") from exc
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    role_resp = supabase.table("user_roles").select("role").eq("user_id", user_id).limit(1).execute()
    role = role_resp.data[0]["role"] if role_resp.data else "viewer"
    return {"id": user_id, "role": role, "email": payload.get("email")}


def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return dep
