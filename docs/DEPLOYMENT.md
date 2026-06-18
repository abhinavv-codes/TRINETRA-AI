# Deployment Guide

## Production Deployment

### Prerequisites
- Azure account with active subscription
- Azure CLI installed
- kubectl installed
- Docker Registry (Azure Container Registry)

---

## Step 1: Containerize Application

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18 as builder
WORKDIR /app
COPY frontend/package*.json .
RUN npm install
COPY frontend .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build images:
```bash
docker build -f backend/Dockerfile -t trinetra-backend:1.0 .
docker build -f frontend/Dockerfile -t trinetra-frontend:1.0 .
```

---

## Step 2: Azure Infrastructure

### Create Resource Group
```bash
az group create --name trinetra-rg --location eastus
```

### Create Container Registry
```bash
az acr create --resource-group trinetra-rg \
  --name trinetraacr --sku Basic
```

### Push Images
```bash
az acr build --registry trinetraacr \
  --image trinetra-backend:1.0 -f backend/Dockerfile .

az acr build --registry trinetraacr \
  --image trinetra-frontend:1.0 -f frontend/Dockerfile .
```

### Create AKS Cluster
```bash
az aks create --resource-group trinetra-rg \
  --name trinetra-aks \
  --node-count 3 \
  --vm-set-type VirtualMachineScaleSets \
  --load-balancer-sku standard \
  --enable-managed-identity

az aks get-credentials --resource-group trinetra-rg \
  --name trinetra-aks
```

### Create Managed PostgreSQL
```bash
az postgres flexible-server create \
  --resource-group trinetra-rg \
  --name trinetra-db \
  --admin-user pgadmin \
  --admin-password YourSecurePassword123! \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --storage-size 32
```

---

## Step 3: Kubernetes Deployment

### Create Namespace
```bash
kubectl create namespace trinetra
```

### Create Secrets
```bash
kubectl create secret generic db-secret \
  --from-literal=password='YourSecurePassword123!' \
  -n trinetra

kubectl create secret docker-registry acr-secret \
  --docker-server=trinetraacr.azurecr.io \
  --docker-username=<username> \
  --docker-password=<password> \
  -n trinetra
```

### Deploy Services (example manifests in `k8s/`)
```bash
kubectl apply -f k8s/backend-deployment.yaml -n trinetra
kubectl apply -f k8s/frontend-deployment.yaml -n trinetra
kubectl apply -f k8s/backend-service.yaml -n trinetra
kubectl apply -f k8s/frontend-service.yaml -n trinetra
```

### Enable Ingress
```bash
kubectl apply -f k8s/ingress.yaml -n trinetra
```

---

## Step 4: Configure DNS

Get LoadBalancer IP:
```bash
kubectl get svc -n trinetra
```

Create DNS record pointing to LoadBalancer IP:
```
api.trinetra.ai → API IP
app.trinetra.ai → Frontend IP
```

---

## Step 5: Enable SSL/TLS

Use cert-manager:
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

kubectl apply -f k8s/certificate.yaml -n trinetra
```

---

## Monitoring

### Application Insights
```bash
az monitor app-insights component create \
  --app trinetra-insights \
  --location eastus \
  --resource-group trinetra-rg
```

### Logs
```bash
kubectl logs -f deployment/trinetra-backend -n trinetra
kubectl logs -f deployment/trinetra-frontend -n trinetra
```

---

## Cost Optimization

- Use Spot VMs for non-critical workloads
- Auto-scaling policies
- Reserved instances for predictable load
- CDN for frontend static assets

---

## Backup Strategy

- PostgreSQL automated backups (7 days)
- Application configuration backups
- Model weights backups to Blob Storage

---

## Rollback Procedure

```bash
# Rollout to previous version
kubectl rollout undo deployment/trinetra-backend -n trinetra

# View history
kubectl rollout history deployment/trinetra-backend -n trinetra
```

---

## Performance Targets

- API response time: < 200ms (p95)
- Frontend load time: < 2s
- Detection latency: < 1s per image
- 99.9% uptime SLA
