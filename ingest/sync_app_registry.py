import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path
from git import Repo
from db.db_helper import get_collection
from config import APP_REGISTRY_REPO, APP_REGISTRY_BRANCH, COLL_APP_REGISTRY, COLL_APPS, COLL_KV

def sync_app_registry():
    print(f"[APP_REG] Syncing from {APP_REGISTRY_REPO}")
    repo_path = Path(APP_REGISTRY_REPO)
    if not repo_path.exists():
        print(f"[APP_REG] ERROR: {repo_path} not found. Clone your app-registry repo first.")
        return
    
    # Pull latest
    repo = Repo(repo_path)
    origin = repo.remotes.origin
    origin.pull(APP_REGISTRY_BRANCH)
    
    reg_col = get_collection(COLL_APP_REGISTRY)
    apps_col = get_collection(COLL_APPS)
    kv_col = get_collection(COLL_KV)
    
    count = 0
    for json_file in repo_path.glob("*.json"):
        with open(json_file) as f:
            data = json.load(f)
        
        app_id = data.get("app_id")
        if not app_id:
            continue
        
        # Upsert raw JSON
        reg_col.update_one({"app_id": app_id}, {"$set": {"json_content": data}}, upsert=True)
        
        # Sync KVs from JSON
        for key in ["deployment_service_adopted", "standard_pipeline_adopted", "api_catalog_registered", "api_inventorized"]:
            if key in data:
                kv_col.update_one({"app_id": app_id, "key": key}, {"$set": {"value": data[key]}}, upsert=True)
        
        count += 1
    
    print(f"[APP_REG] Synced {count} app JSON files")

if __name__ == "__main__":
    sync_app_registry()
