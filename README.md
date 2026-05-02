# DevOps DPI — MongoDB Version

**Full-featured release frequency gamification platform** with:
- 24h automated data pipeline
- App registry JSON sync from Git
- Admin panel for CRUD operations
- Read-only JSON viewer for app owners

## Quick Start

1. Install MongoDB (see MONGODB_SETUP.md)
2. Install Python dependencies: `pip install -r requirements.txt`
3. Create `.env` file (template in MONGODB_SETUP.md)
4. Initialize DB: `python -m db.init_db`
5. Create admin user: `python -m seed.create_admin`
6. Seed data: `python -m seed.seed_data` (edit file first)
7. Start API: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
8. Start scheduler: `python scheduler.py`

**Dashboard:** http://localhost:8000  
**Admin Panel:** http://localhost:8000/admin

See MONGODB_SETUP.md for detailed MongoDB installation guide.
