'''Create admin user'''
import sys, os, getpass
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_helper import get_collection
from config import COLL_ADMIN_USERS
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ")
    
    col = get_collection(COLL_ADMIN_USERS)
    if col.find_one({"username": username}):
        print(f"User {username} already exists")
        return
    
    col.insert_one({
        "username": username,
        "hashed_password": pwd_context.hash(password),
        "is_active": True
    })
    print(f"✓ Admin user {username} created")

if __name__ == "__main__":
    create_admin()
