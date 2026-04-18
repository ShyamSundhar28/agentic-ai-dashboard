# Stage 1: Build React Dashboard
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Python
FROM python:3.12-slim
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files and build output
COPY . .
COPY --from=build-stage /app/dist /app/dist

# Expose port
EXPOSE 8080

# Run the FastAPI server
CMD ["python", "app/main.py"]
