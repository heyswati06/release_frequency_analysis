"""
config.py — Central configuration for DevOps DPI Platform (MongoDB)
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── MONGODB ──────────────────────────────────────────────────────────────────
MONGO_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB   = os.getenv("MONGO_DB", "devops_dpi")

# Collections (equivalent to SQL tables)
COLL_APPS          = "apps"
COLL_REPOS         = "app_repos"
COLL_HEADCOUNT     = "app_headcount"
COLL_KV            = "app_kv"
COLL_RF_SNAPSHOTS  = "rf_snapshots"
COLL_GIT_HYGIENE   = "git_hygiene"
COLL_DOC_HYGIENE   = "doc_hygiene"
COLL_DPI_SCORES    = "dpi_scores"
COLL_APP_REGISTRY  = "app_registry_json"  # stores raw JSON from Git
COLL_ADMIN_USERS   = "admin_users"

# ── APP REGISTRY GIT REPO ────────────────────────────────────────────────────
# Path to your local clone of the app registry repo (one JSON file per app)
APP_REGISTRY_REPO  = os.getenv("APP_REGISTRY_REPO", "/path/to/app-registry-repo")
APP_REGISTRY_BRANCH= os.getenv("APP_REGISTRY_BRANCH", "main")

# ── DASH API ─────────────────────────────────────────────────────────────────
DASH_API_URL       = os.getenv("DASH_API_URL", "https://your-dash-api/export/changes")
DASH_API_KEY       = os.getenv("DASH_API_KEY", "")
DASH_API_HEADERS   = {"Authorization": f"Bearer {DASH_API_KEY}"}

DASH_COL_APP_ID          = os.getenv("DASH_COL_APP_ID",     "Application ID")
DASH_COL_ASSIGN_GROUP    = os.getenv("DASH_COL_AG",         "Assignment Group")
DASH_COL_ENVIRONMENT     = os.getenv("DASH_COL_ENV",        "Environment")
DASH_COL_PLANNED_START   = os.getenv("DASH_COL_START",      "Planned Start Date")
DASH_COL_ACTUAL_END      = os.getenv("DASH_COL_END",        "Actual End Date")
DASH_COL_CHANGE_STATE    = os.getenv("DASH_COL_STATE",      "State")
DASH_ENV_PROD_VALUE      = os.getenv("DASH_ENV_PROD",       "Production")
DASH_STATE_CLOSED_VALUE  = os.getenv("DASH_STATE_CLOSED",   "Closed")

# ── GITHUB ───────────────────────────────────────────────────────────────────
GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = "https://api.github.com"
GITHUB_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
STALE_PR_DAYS = int(os.getenv("STALE_PR_DAYS", "30"))

# ── RF TARGET ────────────────────────────────────────────────────────────────
RF_TARGET_2026 = int(os.getenv("RF_TARGET_2026", "280"))

# ── DPI SCORING WEIGHTS ──────────────────────────────────────────────────────
SCORE_WEIGHT_RF          = 35
SCORE_WEIGHT_LTTD        = 25
SCORE_WEIGHT_GIT_HYGIENE = 20
SCORE_WEIGHT_DOC_HYGIENE = 10
SCORE_WEIGHT_ADOPTION    = 10

# ── TIER THRESHOLDS ──────────────────────────────────────────────────────────
TIER_PLATINUM   = 85
TIER_GOLD       = 70
TIER_SILVER     = 50
TIER_BRONZE     = 30

# ── LTTD SCORING BANDS ───────────────────────────────────────────────────────
LTTD_BANDS = [
    (3,   25),
    (7,   20),
    (14,  15),
    (21,  10),
    (30,   5),
    (9999, 2),
]

# ── SCHEDULER ────────────────────────────────────────────────────────────────
SCHEDULER_HOUR   = int(os.getenv("SCHEDULER_HOUR",   "2"))
SCHEDULER_MINUTE = int(os.getenv("SCHEDULER_MINUTE", "0"))

# ── ADOPTION KV KEYS ─────────────────────────────────────────────────────────
ADOPTION_KEYS = [
    "deployment_service_adopted",
    "standard_pipeline_adopted",
    "api_catalog_registered",
    "api_inventorized",
]

# ── ADMIN AUTH ───────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours
