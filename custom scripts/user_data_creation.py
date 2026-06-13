import os
import sys
import argparse
import random
import string

# Ensure the script can find the project directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def generate_random_string(length=8):
    """Generate a random lowercase string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def create_random_users(count):
    users_to_create = []
    print(f"Generating {count} random users...")
    
    for _ in range(count):
        username = generate_random_string(10)
        email = f"{username}@example.com"
        password = "password123" # Hardcoded password for ease of access
        
        user = User(
            username=username,
            email=email,
            password=make_password(password)
        )
        users_to_create.append(user)
        
    # Bulk create users to optimize database performance
    created_users = User.objects.bulk_create(users_to_create)
    print(f"Successfully created {len(created_users)} users.")
    
    if created_users:
        readme_path = os.path.join(project_root, "README.md")
        with open(readme_path, "a") as f:
            f.write("\n### Recently Generated Test Accounts\n")
            for u in created_users:
                f.write(f"- **Username:** `{u.username}` | **Password:** `password123`\n")
        
        print("Example login credentials: ")
        print(f"Username: {created_users[0].username}")
        print(f"Password: password123")
        print(f"\nSaved generated accounts to README.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk create random users.")
    parser.add_argument("count", type=int, help="Number of users to create")
    args = parser.parse_args()
    
    if args.count <= 0:
        print("Count must be greater than 0.")
    else:
        create_random_users(args.count)
