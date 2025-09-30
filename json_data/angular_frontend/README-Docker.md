# 🐳 Running SmartTactic Frontend with Docker

This guide will help you run the Angular application using Docker, which eliminates the need to install Node.js directly on your system.

## Prerequisites

### 1. Install Docker Desktop

1. **Download Docker Desktop**: Go to https://docker.com/get-started/
2. **Download for Windows**: Click "Download for Windows"
3. **Install Docker Desktop**: Run the installer as Administrator
4. **Start Docker Desktop**: Launch the application and wait for it to start
5. **Verify Installation**: Open PowerShell and run `docker --version`

## Quick Start

### Option 1: Using the Batch Script (Easiest)
```bash
# Navigate to the angular_frontend directory
cd json_data/angular_frontend

# Run the batch script
run-docker.bat
```

### Option 2: Using Docker Commands
```bash
# Navigate to the angular_frontend directory
cd json_data/angular_frontend

# Build and start the application
docker-compose up --build
```

### Option 3: Manual Docker Commands
```bash
# Pull the Node.js image
docker pull node:22-alpine

# Build the image
docker build -t smart-tactic-frontend .

# Run the container
docker run -it --rm -p 4200:4200 -v ${PWD}:/app -v /app/node_modules smart-tactic-frontend
```

## Access the Application

Once the container is running, open your browser and navigate to:
- **http://localhost:4200**

## Stopping the Application

- **Press Ctrl+C** in the terminal to stop the application
- Or run: `docker-compose down`

## Troubleshooting

### Docker Not Found
```
docker: command not found
```
**Solution**: Install Docker Desktop and make sure it's running.

### Port Already in Use
```
Error: listen EADDRINUSE: address already in use :::4200
```
**Solution**: Stop any other applications using port 4200, or change the port in docker-compose.yml.

### Permission Issues (Windows)
If you get permission errors, try:
1. Run PowerShell as Administrator
2. Enable WSL 2 in Docker Desktop settings
3. Restart Docker Desktop

## Development with Hot Reload

The Docker setup includes hot reload, so any changes you make to the source code will automatically refresh the browser.

## File Structure
```
angular_frontend/
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── run-docker.bat          # Windows batch script
├── .dockerignore          # Files to ignore in Docker
└── README-Docker.md       # This file
```
