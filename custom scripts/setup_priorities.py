import os
import sys
import django

# Add the project root to the python path so it can find 'config'
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.tasks.models import Priority

def run():
    default_priorities = [
        {"name": "Low", "color": "#28a745", "order": 1, "weightage": 10},
        {"name": "Medium", "color": "#ffc107", "order": 2, "weightage": 20},
        {"name": "High", "color": "#dc3545", "order": 3, "weightage": 30},
    ]

    print("Setting up default priorities...")
    
    for p in default_priorities:
        obj, created = Priority.objects.get_or_create(
            name=p['name'], 
            defaults=p
        )
        if created:
            print(f"✅ Created priority: {p['name']}")
        else:
            print(f"ℹ️ Priority already exists: {p['name']}")
            
    print("Done!")

if __name__ == "__main__":
    run()
