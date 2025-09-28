# 🔌 Port Configuration Guide

BBB Medical System port configuration and setup guide.

## 📊 Port Mapping

| Service | Port | Description | Access URL |
|---------|------|-------------|------------|
| **Backend API** | 8082 | FastAPI backend | http://localhost:8082 |
| **Patient Frontend** | 3000 | Patient interface | http://localhost:3000 |
| **Doctor Frontend** | 3001 | Doctor interface | http://localhost:3001 |
| **Unified Frontend** | 5173 | Single frontend (dev) | http://localhost:5173 |

## 🚀 Setup Options

### Option 1: Separate Frontend Services (Recommended)

#### Development
```bash
# Terminal 1: Backend API
make api

# Terminal 2: Patient Frontend
make ui-patient

# Terminal 3: Doctor Frontend
make ui-doctor
```

#### Docker
```bash
# Build and start separate services
make docker-build
make docker-up-separate
```

**Access URLs:**
- API: http://localhost:8082
- Patient: http://localhost:3000
- Doctor: http://localhost:3001

### Option 2: Unified Frontend Service

#### Development
```bash
# Single command for all services
make dev
```

#### Docker
```bash
# Build and start unified services
make docker-build
make docker-up
```

**Access URLs:**
- API: http://localhost:8082
- Frontend: http://localhost:5173

## 🔧 Configuration Files

### Docker Compose

#### Unified Services (`docker-compose.yml`)
```yaml
services:
  api:
    ports:
      - "8082:8082"
  frontend:
    ports:
      - "5173:5173"
```

#### Separate Services (`docker-compose-separate.yml`)
```yaml
services:
  api:
    ports:
      - "8082:8082"
  patient-frontend:
    ports:
      - "3000:3000"
  doctor-frontend:
    ports:
      - "3001:3001"
```

### Package.json Scripts
```json
{
  "scripts": {
    "start:patient": "next start -p 3000",
    "start:doctor": "next start -p 3001",
    "dev:patient": "next dev -p 3000 --turbopack",
    "dev:doctor": "next dev -p 3001 --turbopack"
  }
}
```

## 🛠️ Development Workflow

### Local Development

#### Start All Services
```bash
# Option 1: Unified (single frontend)
make dev

# Option 2: Separate (recommended)
make api &          # Backend API (8082)
make ui-patient &   # Patient Frontend (3000)
make ui-doctor &    # Doctor Frontend (3001)
```

#### Start Individual Services
```bash
# Backend only
make api

# Patient frontend only
make ui-patient

# Doctor frontend only
make ui-doctor
```

### Docker Development

#### Build Images
```bash
# Build all images
make docker-build

# Build specific image
docker build -f docker/Dockerfile.patient -t bbb-patient .
docker build -f docker/Dockerfile.doctor -t bbb-doctor .
```

#### Run Services
```bash
# Unified services
make docker-up

# Separate services (recommended)
make docker-up-separate
```

## 🔍 Troubleshooting

### Port Conflicts

#### Check Port Usage
```bash
# Check if ports are in use
lsof -i :3000
lsof -i :3001
lsof -i :8082
lsof -i :5173
```

#### Kill Processes
```bash
# Kill process using specific port
kill -9 $(lsof -ti:3000)
kill -9 $(lsof -ti:3001)
kill -9 $(lsof -ti:8082)
```

### Docker Issues

#### Clean Docker Cache
```bash
# Remove unused containers and images
docker system prune -f

# Remove specific images
docker rmi bbb-medical-api bbb-medical-patient bbb-medical-doctor
```

#### Rebuild Services
```bash
# Stop services
make docker-down-separate

# Rebuild and start
make docker-build
make docker-up-separate
```

### Service Not Starting

#### Check Logs
```bash
# Docker logs
make docker-logs-separate

# Individual service logs
docker logs bbb-medical-api
docker logs bbb-medical-patient
docker logs bbb-medical-doctor
```

#### Check Health
```bash
# API health check
curl http://localhost:8082/health

# Frontend health check
curl http://localhost:3000
curl http://localhost:3001
```

## 📈 Performance Optimization

### Port Configuration

#### Development
- Use different ports for each service
- Enable hot reload for frontend services
- Use `--turbopack` for faster Next.js builds

#### Production
- Use reverse proxy (nginx) for port 80/443
- Configure SSL certificates
- Set up load balancing if needed

### Resource Management

#### Memory Usage
```bash
# Check Docker resource usage
docker stats

# Check system resources
htop
```

#### Port Binding
```bash
# Bind to specific interface
docker run -p 127.0.0.1:3000:3000 bbb-patient
docker run -p 127.0.0.1:3001:3001 bbb-doctor
```

## 🔒 Security Considerations

### Port Security
- Use firewall rules to restrict access
- Bind to localhost only in development
- Use HTTPS in production

### Docker Security
```bash
# Run containers with limited privileges
docker run --user 1000:1000 bbb-patient

# Use read-only filesystem
docker run --read-only bbb-patient
```

## 📚 Additional Resources

### Documentation
- [Development Guide](DEVELOPMENT.md)
- [API Documentation](API.md)
- [Docker Guide](docker/README.md)

### Commands Reference
```bash
# Help
make help

# All available targets
make

# Specific service commands
make ui-patient
make ui-doctor
make docker-up-separate
```
