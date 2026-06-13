# 1. Use the official lightweight Python image
FROM python:3.11-slim

# 2. Set environment variables to make Python run perfectly in Docker
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Install system dependencies (needed for compiling certain Python packages)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 6. Copy the rest of your application code
COPY . .

# 7. Expose the port (Documentation purpose)
EXPOSE 8000