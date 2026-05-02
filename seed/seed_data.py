import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_helper import get_collection
from config import *

SEED_DATA = {
    "apps": [
        {"app_id": "APP-001", "app_name": "Payment Processor", "assignment_group": "PAY-CICD-AG", "deploy_type": "Automated", "segment": "PERFORMING", "prod_releases_expected": 1},
        {"app_id": "APP-002", "app_name": "Analytics Engine", "assignment_group": "ANA-CICD-AG", "deploy_type": "Automated", "segment": "AUTO-BATCHING", "prod_releases_expected": 1},
        # ADD ALL 52 APPS HERE
    ],
    "headcount": [
        {"app_id": "APP-001", "release_hc": 10, "non_release_hc": 2},
        {"app_id": "APP-002", "release_hc": 9, "non_release_hc": 3},
    ],
    "repos": [
        {"app_id": "APP-001", "repo_owner": "myorg", "repo_name": "payment-processor"},
        {"app_id": "APP-002", "repo_owner": "myorg", "repo_name": "analytics-engine"},
    ],
}

def seed():
    apps_col = get_collection(COLL_APPS)
    for app in SEED_DATA["apps"]:
        apps_col.update_one({"app_id": app["app_id"]}, {"$set": app}, upsert=True)
    print(f"Seeded {len(SEED_DATA['apps'])} apps")
    
    hc_col = get_collection(COLL_HEADCOUNT)
    for hc in SEED_DATA["headcount"]:
        hc_col.update_one({"app_id": hc["app_id"]}, {"$set": hc}, upsert=True)
    print(f"Seeded {len(SEED_DATA['headcount'])} headcount records")
    
    repos_col = get_collection(COLL_REPOS)
    for repo in SEED_DATA["repos"]:
        repos_col.update_one({"app_id": repo["app_id"], "repo_name": repo["repo_name"]}, {"$set": repo}, upsert=True)
    print(f"Seeded {len(SEED_DATA['repos'])} repos")

if __name__ == "__main__":
    seed()
