# 🐳 Docker Configuration

This directory contains Docker configurations for the BBB Medical System.

## 📁 Files

- `Dockerfile` - Backend API container
- `Dockerfile.patient` - Patient frontend container (Port 3000)
- `Dockerfile.doctor` - Doctor frontend container (Port 3001)
- `docker-compose.yml` - Unified services (single frontend)
- `docker-compose-separate.yml` - Separate frontend services
- `.dockerignore` - Files to exclude from Docker builds

## 🚀 Quick Start

### Unified Services (Single Frontend)
```bash
# Build and start all services
make docker-build
make docker-up

# Access:
# - API: http://localhost:8082
# - Frontend: http://localhost:5173
```

### Separate Frontend Services (Recommended)
```bash
# Build and start separate services
make docker-build
make docker-up-separate

# Access:
# - API: http://localhost:8082
# - Patient Frontend: http://localhost:3000
# - Doctor Frontend: http://localhost:3001
```

## 🔧 Service Configuration

### Backend API (Port 8082)
- FastAPI application
- SQLite database
- RAG system
- Health checks

### Patient Frontend (Port 3000)
- Next.js application
- Patient interface
- Symptom input forms
- Report viewing

### Doctor Frontend (Port 3001)
- Next.js application
- Doctor dashboard
- Report analysis
- Code generation

## 🛠️ Development

### Local Development
```bash
# Run individual services
make api &          # Backend API
make ui-patient &   # Patient frontend
make ui-doctor &    # Doctor frontend
```

### Docker Development
```bash
# Build specific service
docker build -f docker/Dockerfile.patient -t bbb-patient .
docker build -f docker/Dockerfile.doctor -t bbb-doctor .

# Run specific service
docker run -p 3000:3000 bbb-patient
docker run -p 3001:3001 bbb-doctor
```

## 📊 Port Mapping

| Service | Port | Description |
|---------|------|-------------|
| API | 8082 | Backend API |
| Patient | 3000 | Patient interface |
| Doctor | 3001 | Doctor interface |
| Unified | 5173 | Single frontend (dev) |

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 3001, 8082 are available
2. **Build failures**: Check Docker daemon is running
3. **Service not starting**: Check logs with `make docker-logs-separate`

### Useful Commands

```bash
# View logs
make docker-logs-separate

# Stop services
make docker-down-separate

# Rebuild services
make docker-build
make docker-up-separate

# Clean up
docker system prune -f
```
