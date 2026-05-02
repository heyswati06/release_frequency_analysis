'''MongoDB index creation'''
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_helper import get_db
from config import *

def init_db():
    db = get_db()
    
    # Apps
    db[COLL_APPS].create_index("app_id", unique=True)
    db[COLL_APPS].create_index("assignment_group")
    
    # Repos
    db[COLL_REPOS].create_index([("app_id", 1), ("repo_name", 1)], unique=True)
    
    # RF snapshots
    db[COLL_RF_SNAPSHOTS].create_index([("app_id", 1), ("snapshot_date", -1)])
    
    # DPI scores
    db[COLL_DPI_SCORES].create_index([("app_id", 1), ("snapshot_date", -1)])
    db[COLL_DPI_SCORES].create_index([("total_score", -1)])
    
    # Git hygiene
    db[COLL_GIT_HYGIENE].create_index([("app_id", 1), ("snapshot_date", -1)])
    
    # App registry JSON
    db[COLL_APP_REGISTRY].create_index("app_id", unique=True)
    
    # Admin users
    db[COLL_ADMIN_USERS].create_index("username", unique=True)
    
    print(f"[DB] Indexes created in {MONGO_DB}")

if __name__ == "__main__":
    init_db()
