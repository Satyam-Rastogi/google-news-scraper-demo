# Deployment Guide

This directory contains deployment configurations for the Google News Scraper API.

## Directory Structure

```
deployment/
├── docker/                   # Docker deployment
│   ├── Dockerfile           # Multi-stage Docker build
│   ├── docker-compose.yml   # Docker Compose configuration
│   └── nginx.conf           # Nginx reverse proxy config
├── kubernetes/              # Kubernetes deployment
│   └── deployment.yaml      # K8s manifests
└── scripts/                 # Deployment scripts
    ├── deploy.sh            # Deploy script
    ├── stop.sh              # Stop script
    └── logs.sh              # Logs script
```

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. **Deploy with Docker Compose:**
```bash
# Deploy the application
./deployment/scripts/deploy.sh

# Stop the application
./deployment/scripts/stop.sh

# View logs
./deployment/scripts/logs.sh
```

2. **Manual Docker Compose:**
```bash
cd deployment/docker
docker-compose up --build -d
```

3. **Access the API:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health/

### Environment Variables

You can customize the deployment by setting environment variables in `docker-compose.yml`:

```yaml
environment:
  - HOST=0.0.0.0
  - PORT=8000
  - DEBUG=false
  - LOG_LEVEL=INFO
  - API_PREFIX=/api/v1
  - ENABLE_VERSIONING=true
  - DEFAULT_MAX_RESULTS=50
  - MAX_RESULTS_LIMIT=100
  - REQUEST_TIMEOUT=30
  - REQUEST_DELAY=1.0
  - DEFAULT_OUTPUT_FORMAT=json
  - OUTPUT_DIRECTORY=artifacts/data/scraped
  - LOGS_DIRECTORY=logs
  - REDIS_HOST=redis
  - REDIS_PORT=6379
  - REDIS_DB=0
  - REDIS_PASSWORD=
  - ENABLE_CACHE=true
  - CACHE_TTL=3600
```

### Services

The deployment includes:

- **news-scraper-api**: Main FastAPI application
- **redis**: Redis cache for performance optimization
- **nginx**: Reverse proxy with security headers and rate limiting

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster
- kubectl configured

### Deploy to Kubernetes

1. **Build and push Docker image:**
```bash
# Build the image
docker build -f deployment/docker/Dockerfile -t news-scraper-api:latest .

# Push to registry (replace with your registry)
docker tag news-scraper-api:latest your-registry/news-scraper-api:latest
docker push your-registry/news-scraper-api:latest
```

2. **Deploy to Kubernetes:**
```bash
kubectl apply -f deployment/kubernetes/deployment.yaml
```

3. **Check deployment:**
```bash
kubectl get pods
kubectl get services
kubectl get pvc
```

4. **Access the API:**
```bash
# Get external IP
kubectl get service news-scraper-api-service

# Port forward for local access
kubectl port-forward service/news-scraper-api-service 8000:80
```

## Production Considerations

### Security
- ✅ Non-root user in container
- ✅ Security headers in Nginx
- ✅ Rate limiting configured
- ✅ Health checks enabled

### Monitoring
- ✅ Health check endpoints
- ✅ Structured logging
- ✅ Request timing headers

### Scalability
- ✅ Horizontal scaling with Kubernetes
- ✅ Load balancing with Nginx
- ✅ Persistent storage for data

### Performance
- ✅ Multi-stage Docker build
- ✅ Connection pooling ready
- ✅ Resource limits configured

## Troubleshooting

### Common Issues

1. **Container won't start:**
```bash
# Check logs
docker-compose logs news-scraper-api

# Check health
curl http://localhost:8000/health/
```

2. **Port conflicts:**
```bash
# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

3. **Permission issues:**
```bash
# Make scripts executable
chmod +x deployment/scripts/*.sh
```

### Health Checks

- **Liveness:** `GET /health/live`
- **Readiness:** `GET /health/ready`
- **General:** `GET /health/`

## Development vs Production

### Development
- Use `DEBUG=true`
- Mount source code as volume
- Enable hot reload

### Production
- Use `DEBUG=false`
- Build optimized image
- Enable all security features
- Use external database (future)
