"""
FastAPI backend - MongoDB version with Admin CRUD endpoints
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from pathlib import Path
from jose import JWTError, jwt
from passlib.context import CryptContext

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_helper import get_collection
from config import *

app = FastAPI(title="DevOps DPI - MongoDB")
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dashboard HTML paths
DASHBOARD_PATH = Path(__file__).parent.parent / "dashboard" / "index.html"
ADMIN_PATH = Path(__file__).parent.parent / "dashboard" / "admin.html"

# Auth helpers
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# === PUBLIC ENDPOINTS (Dashboard) ===

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    if DASHBOARD_PATH.exists():
        return HTMLResponse(content=DASHBOARD_PATH.read_text())
    return HTMLResponse("<h1>Dashboard not found</h1>", status_code=404)

@app.get("/api/portfolio")
def portfolio_summary():
    apps_col = get_collection(COLL_APPS)
    rf_col = get_collection(COLL_RF_SNAPSHOTS)
    dpi_col = get_collection(COLL_DPI_SCORES)
    
    total_apps = apps_col.count_documents({})
    
    # Latest snapshot date
    latest = rf_col.find_one(sort=[("snapshot_date", -1)])
    snap_date = latest["snapshot_date"] if latest else datetime.now().date().isoformat()
    
    # Average RF
    pipeline = [
        {"$match": {"snapshot_date": snap_date}},
        {"$group": {"_id": None, "avg_rf": {"$avg": "$rf_annualised"}, "total_rel": {"$sum": "$release_count"}}}
    ]
    rf_agg = list(rf_col.aggregate(pipeline))
    avg_rf = round(rf_agg[0]["avg_rf"], 1) if rf_agg else 0
    total_releases = rf_agg[0]["total_rel"] if rf_agg else 0
    
    # Tier counts
    tier_pipeline = [{"$match": {"snapshot_date": snap_date}}, {"$group": {"_id": "$tier", "count": {"$sum": 1}}}]
    tier_counts = {t["_id"]: t["count"] for t in dpi_col.aggregate(tier_pipeline)}
    
    # Status counts
    status_pipeline = [{"$match": {"snapshot_date": snap_date}}, {"$group": {"_id": "$status", "count": {"$sum": 1}}}]
    status_counts = {s["_id"]: s["count"] for s in rf_col.aggregate(status_pipeline)}
    
    return {
        "snapshot_date": snap_date,
        "total_apps": total_apps,
        "rf_target": RF_TARGET_2026,
        "avg_rf": avg_rf,
        "total_releases": total_releases,
        "tier_counts": tier_counts,
        "status_counts": status_counts,
    }

@app.get("/api/leaderboard")
def leaderboard(tier: Optional[str] = None, search: Optional[str] = None):
    apps_col = get_collection(COLL_APPS)
    rf_col = get_collection(COLL_RF_SNAPSHOTS)
    hc_col = get_collection(COLL_HEADCOUNT)
    dpi_col = get_collection(COLL_DPI_SCORES)
    
    latest = rf_col.find_one(sort=[("snapshot_date", -1)])
    snap_date = latest["snapshot_date"] if latest else datetime.now().date().isoformat()
    
    # Build aggregation pipeline
    pipeline = [
        {"$lookup": {"from": COLL_HEADCOUNT, "localField": "app_id", "foreignField": "app_id", "as": "hc"}},
        {"$lookup": {"from": COLL_RF_SNAPSHOTS, "let": {"aid": "$app_id"}, 
                     "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$app_id", "$$aid"]}, {"$eq": ["$snapshot_date", snap_date]}]}}}],
                     "as": "rf"}},
        {"$lookup": {"from": COLL_DPI_SCORES, "let": {"aid": "$app_id"},
                     "pipeline": [{"$match": {"$expr": {"$and": [{"$eq": ["$app_id", "$$aid"]}, {"$eq": ["$snapshot_date", snap_date]}]}}}],
                     "as": "dpi"}},
        {"$addFields": {
            "total_hc": {"$sum": [{"$arrayElemAt": ["$hc.release_hc", 0]}, {"$arrayElemAt": ["$hc.non_release_hc", 0]}]},
            "rf_data": {"$arrayElemAt": ["$rf", 0]},
            "dpi_data": {"$arrayElemAt": ["$dpi", 0]},
        }},
        {"$addFields": {
            "rf_annualised": {"$ifNull": ["$rf_data.rf_annualised", 0]},
            "total_score": {"$ifNull": ["$dpi_data.total_score", 0]},
            "tier": {"$ifNull": ["$dpi_data.tier", "Developing"]},
        }},
    ]
    
    # Filters
    match_stage = {}
    if tier and tier != "All":
        match_stage["tier"] = tier
    if search:
        match_stage["$or"] = [
            {"app_name": {"$regex": search, "$options": "i"}},
            {"app_id": {"$regex": search, "$options": "i"}},
            {"assignment_group": {"$regex": search, "$options": "i"}},
        ]
    
    if match_stage:
        pipeline.append({"$match": match_stage})
    
    pipeline.append({"$sort": {"total_score": -1, "rf_annualised": -1}})
    
    result = []
    for i, doc in enumerate(apps_col.aggregate(pipeline), 1):
        rf_data = doc.get("rf_data", {})
        dpi_data = doc.get("dpi_data", {})
        result.append({
            "rank": i,
            "app_id": doc["app_id"],
            "app_name": doc["app_name"],
            "assignment_group": doc["assignment_group"],
            "deploy_type": doc.get("deploy_type", ""),
            "segment": doc.get("segment", ""),
            "total_hc": doc.get("total_hc", 0),
            "rf_annualised": doc.get("rf_annualised", 0),
            "lttd_avg_days": rf_data.get("lttd_avg_days"),
            "rf_status": rf_data.get("status", ""),
            "release_count": rf_data.get("release_count", 0),
            "total_score": doc.get("total_score", 0),
            "rf_score": dpi_data.get("rf_score", 0),
            "lttd_score": dpi_data.get("lttd_score", 0),
            "git_score": dpi_data.get("git_score", 0),
            "doc_score": dpi_data.get("doc_score", 0),
            "adoption_score": dpi_data.get("adoption_score", 0),
            "tier": doc.get("tier", "Developing"),
            "badges": dpi_data.get("badges", []),
        })
    
    return result

@app.get("/api/app/{app_id}")
def app_detail(app_id: str):
    apps_col = get_collection(COLL_APPS)
    app = apps_col.find_one({"app_id": app_id})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    app.pop("_id", None)
    
    # Get all related data
    hc_col = get_collection(COLL_HEADCOUNT)
    repos_col = get_collection(COLL_REPOS)
    kv_col = get_collection(COLL_KV)
    rf_col = get_collection(COLL_RF_SNAPSHOTS)
    dpi_col = get_collection(COLL_DPI_SCORES)
    git_col = get_collection(COLL_GIT_HYGIENE)
    doc_col = get_collection(COLL_DOC_HYGIENE)
    registry_col = get_collection(COLL_APP_REGISTRY)
    
    latest = rf_col.find_one(sort=[("snapshot_date", -1)])
    snap_date = latest["snapshot_date"] if latest else datetime.now().date().isoformat()
    
    hc = hc_col.find_one({"app_id": app_id}) or {}
    hc.pop("_id", None)
    
    repos = list(repos_col.find({"app_id": app_id}, {"_id": 0}))
    kvs = {kv["key"]: kv["value"] for kv in kv_col.find({"app_id": app_id})}
    
    rf_row = rf_col.find_one({"app_id": app_id, "snapshot_date": snap_date}) or {}
    rf_row.pop("_id", None)
    
    dpi_row = dpi_col.find_one({"app_id": app_id, "snapshot_date": snap_date}) or {}
    dpi_row.pop("_id", None)
    
    # Repo hygiene
    git_docs = git_col.find({"app_id": app_id, "snapshot_date": snap_date})
    doc_docs = {d["repo_name"]: d for d in doc_col.find({"app_id": app_id, "snapshot_date": snap_date})}
    
    repo_hygiene = []
    for g in git_docs:
        g.pop("_id", None)
        d = doc_docs.get(g["repo_name"], {})
        d.pop("_id", None)
        repo_hygiene.append({**g, **d})
    
    # App registry JSON
    reg = registry_col.find_one({"app_id": app_id}) or {}
    app_json = reg.get("json_content", {})
    
    return {
        "app": app,
        "headcount": hc,
        "repos": repos,
        "kvs": kvs,
        "rf": rf_row,
        "dpi": dpi_row,
        "repo_hygiene": repo_hygiene,
        "adoption_keys": ADOPTION_KEYS,
        "app_json": app_json,
    }

# === ADMIN ENDPOINTS ===

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel():
    if ADMIN_PATH.exists():
        return HTMLResponse(content=ADMIN_PATH.read_text())
    return HTMLResponse("<h1>Admin panel not found</h1>", status_code=404)

@app.post("/api/admin/login")
def admin_login(body: dict = Body(...)):
    username = body.get("username")
    password = body.get("password")
    
    col = get_collection(COLL_ADMIN_USERS)
    user = col.find_one({"username": username})
    
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/admin/apps")
def admin_list_apps(username: str = Depends(verify_token)):
    col = get_collection(COLL_APPS)
    apps = list(col.find({}, {"_id": 0}))
    return apps

@app.post("/api/admin/apps")
def admin_create_app(body: dict = Body(...), username: str = Depends(verify_token)):
    col = get_collection(COLL_APPS)
    body.setdefault("created_at", datetime.now().isoformat())
    col.insert_one(body)
    return {"status": "created", "app_id": body["app_id"]}

@app.put("/api/admin/apps/{app_id}")
def admin_update_app(app_id: str, body: dict = Body(...), username: str = Depends(verify_token)):
    col = get_collection(COLL_APPS)
    body["updated_at"] = datetime.now().isoformat()
    col.update_one({"app_id": app_id}, {"$set": body})
    return {"status": "updated"}

@app.delete("/api/admin/apps/{app_id}")
def admin_delete_app(app_id: str, username: str = Depends(verify_token)):
    col = get_collection(COLL_APPS)
    col.delete_one({"app_id": app_id})
    return {"status": "deleted"}

@app.get("/api/admin/headcount")
def admin_list_headcount(username: str = Depends(verify_token)):
    col = get_collection(COLL_HEADCOUNT)
    return list(col.find({}, {"_id": 0}))

@app.post("/api/admin/headcount")
def admin_upsert_headcount(body: dict = Body(...), username: str = Depends(verify_token)):
    col = get_collection(COLL_HEADCOUNT)
    col.update_one({"app_id": body["app_id"]}, {"$set": body}, upsert=True)
    return {"status": "ok"}

@app.get("/api/health")
def health():
    return {"status": "ok", "db": MONGO_DB}
