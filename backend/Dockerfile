# =========================
# Stage 1: Build Python Backend
# =========================
FROM python:3.11-alpine AS build

# Set working directory
WORKDIR /backend/functionality

# Install system dependencies (needed for packages like mysqlclient, psycopg2, etc.)
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-dev pkgconfig

# Copy requirements and install dependencies
COPY requirements.txt .

RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy the backend source code into the image
COPY . .

# =========================
# Stage 2: Runtime container
# =========================
FROM python:3.11-alpine

# Set working directory
WORKDIR /backend/functionality

# Copy virtual environment and app files from build stage
COPY --from=build /backend/functionality /backend/functionality

# Expose backend port (e.g. Flask or FastAPI usually uses 8000)
EXPOSE 5001

# Command to start your backend (edit if different)
# Example for Flask:
CMD ["/backend/functionality/venv/bin/python3", "app.py"]
