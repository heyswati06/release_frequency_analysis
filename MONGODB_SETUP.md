# MongoDB Setup Guide for Beginners

## Step 1: Install MongoDB

### On Ubuntu/Debian:
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

### On macOS:
```bash
brew tap mongodb/brew
brew install mongodb-community@7.0
```

### On Windows:
Download installer from: https://www.mongodb.com/try/download/community

## Step 2: Start MongoDB

### Ubuntu/Linux:
```bash
sudo systemctl start mongod
sudo systemctl enable mongod  # auto-start on boot
```

### macOS:
```bash
brew services start mongodb-community@7.0
```

### Windows:
MongoDB runs as a service automatically after installation.

## Step 3: Verify MongoDB is Running
```bash
mongosh
# You should see a MongoDB shell prompt
# Type: show dbs
# Type: exit
```

## Step 4: Create Database and Admin User (Optional but Recommended)

```bash
mongosh

use devops_dpi

db.createUser({
  user: "dpi_admin",
  pwd: "your-secure-password-here",
  roles: [{ role: "readWrite", db: "devops_dpi" }]
})

exit
```

## Step 5: Configure Your Application

Create `.env` file in project root:

```env
# MongoDB
MONGO_URI=mongodb://dpi_admin:your-secure-password-here@localhost:27017/
MONGO_DB=devops_dpi

# App Registry Git Repo (local clone path)
APP_REGISTRY_REPO=/path/to/your/app-registry-repo
APP_REGISTRY_BRANCH=main

# Dash API
DASH_API_URL=https://your-dash-api/export
DASH_API_KEY=your-key

# GitHub
GITHUB_TOKEN=ghp_your_token

# Admin Auth
SECRET_KEY=generate-random-secret-key-here
```

## Step 6: Initialize Collections and Indexes

```bash
python -m db.init_db
```

## Step 7: Create First Admin User

```bash
python -m seed.create_admin
```
You'll be prompted for username and password.

## Step 8: Seed Your Data

Edit `seed/seed_data.py` with your 52 apps, then:
```bash
python -m seed.seed_data
```

## Step 9: Start the API

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Dashboard: http://localhost:8000
Admin Panel: http://localhost:8000/admin

## Step 10: Start the Scheduler

```bash
python scheduler.py
```

## Common MongoDB Commands

```bash
# Connect to MongoDB shell
mongosh

# Switch to your database
use devops_dpi

# List all collections
show collections

# View documents in a collection
db.apps.find().pretty()

# Count documents
db.apps.countDocuments()

# Delete all documents in a collection (careful!)
db.rf_snapshots.deleteMany({})

# Drop entire database (very careful!)
db.dropDatabase()
```

## Troubleshooting

**MongoDB won't start:**
```bash
# Check status
sudo systemctl status mongod

# Check logs
sudo tail -f /var/log/mongodb/mongod.log
```

**Connection refused:**
- Verify MongoDB is running: `sudo systemctl status mongod`
- Check firewall settings
- Verify MONGO_URI in .env matches your setup

**Permission denied:**
- Ensure your user has read/write access to database
- Re-run `db.createUser()` command above
