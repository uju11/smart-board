# Smart Task Board

A robust, Django-based task management board featuring JWT authentication, Ninja API, and a beautiful UI.
Instead of Rest-api used ninja-api, reason being it is faster and easier to use, provides asynchornous operations support
and also provides jwt authentication out of the box.
psycopg2-binary for postgres db.
redis handles the caching.
django-redis handles the cache configuration.
django-ninja-jwt handles the jwt authentication.

no proper front-end technology is used, just a basic html and css for now(Single Page Application).

## Getting Started

1. Ensure Docker and Docker Compose are installed.
2. Run `docker-compose up --build -d` to start the application.
3. Access the web application at `http://127.0.0.1:8000`.
4. API documentation is available at `http://127.0.0.1:8000/api/docs`.

## Accounts for Testing

The following accounts are available for testing the application:

### Admin Account
- **Username:** `admin`
- **Email:** `admin@demo.com`
- **Password:** `admin`

### Test Accounts (Randomly Generated)
If you have run the `user_data_creation.py` script (e.g., `docker-compose exec web python "custom scripts/user_data_creation.py" 5`), the newly created random users will have the password **`password123`**.

*(Run the script to generate unique random usernames).*

## Utilities

- **Bulk User Creation Script:**
  `docker-compose exec web python "custom scripts/user_data_creation.py" <number_of_users>`

### Recently Generated Test Accounts
- **Username:** `tcfagwbdbh` | **Password:** `password123`
- **Username:** `tffhqsfvqg` | **Password:** `password123`
- **Username:** `stydkcsimc` | **Password:** `password123`

### Recently Generated Test Accounts
- **Username:** `flptnjmhgz` | **Password:** `password123`
- **Username:** `blgogyqfgj` | **Password:** `password123`
- **Username:** `dvwwlevnca` | **Password:** `password123`
