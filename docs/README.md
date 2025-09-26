# GearboxGuard: Gearbox Fault Diagnosis Pipeline

GearboxGuard is a scalable microservices-based application for diagnosing faults in gearboxes using machine learning. It simulates vibration signals, extracts features, classifies faults, and provides a web interface for users to run diagnostics. The system is deployed on Kubernetes with automatic scaling via Horizontal Pod Autoscalers (HPAs).

## Features
- **Signal Generation**: Simulates healthy and broken gearbox vibration signals.
- **Feature Extraction**: Processes signals to extract time-domain and frequency-domain features.
- **Fault Classification**: Uses a trained ML model to predict if the gearbox is healthy or faulty.
- **Web Frontend**: User-friendly UI to upload/run diagnostics and view results.
- **Data Storage**: MongoDB for storing signals, features, and predictions.
- **Scaling**: Kubernetes Deployments with HPAs for CPU-based autoscaling (min 2, max 10 replicas per service).
- **API Routing**: NGINX Ingress with regex rewriting for clean URLs (e.g., `/api/signal/test` → `/test`).

## Architecture Overview
See [architecture.md](architecture.md) for detailed diagrams and component interactions.

## Prerequisites
- Docker and Docker Desktop with Kubernetes enabled.
- kubectl installed.
- MongoDB image (pulled automatically).
- Go (optional, for load testing with `hey`).

## Quick Start
1. **Clone and Setup**:
   ```
   git clone <repo>
   cd gearboxGuard
   ```

2. **Build and Push Docker Images** (if not using pre-built):
   ```
   cd signalgenerator && docker build -t ashwin0302/signalgenerator:latest . && docker push ashwin0302/signalgenerator:latest
   cd ../featureextractor && docker build -t ashwin0302/featureextractor:latest . && docker push ashwin0302/featureextractor:latest
   cd ../faultclassifier && docker build -t ashwin0302/faultclassifier:latest . && docker push ashwin0302/faultclassifier:latest
   cd ../frontend && docker build -t ashwin0302/frontend:latest . && docker push ashwin0302/frontend:latest
   ```

3. **Deploy to Kubernetes**:
   ```
   # Apply all K8s manifests
   kubectl apply -f k8s/
   
   # Apply HPAs for autoscaling
   kubectl apply -f k8s/hpa-*.yaml
   ```

4. **Install Metrics Server** (for HPA metrics):
   ```
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

5. **Access the Application**:
   - Port-forward Ingress: `kubectl port-forward svc/ingress-nginx-controller 80:80 -n ingress-nginx`
   - Open http://localhost in browser.
   - Run a diagnosis: Click "Run Broken Sample" → View signal plot → Prediction result.

6. **Scale Manually** (immediate):
   ```
   kubectl scale deployment frontend --replicas=3
   kubectl scale deployment signalgenerator --replicas=5
   # etc.
   ```

7. **Test Autoscaling**:
   - Generate load: Use PowerShell `1..50 | ForEach-Object { Start-Job -ScriptBlock { Invoke-WebRequest -Uri "http://localhost/" -Method Get } }`
   - Monitor: `kubectl get hpa -w` and `kubectl get pods -w`

## End-to-End Flow
1. User selects sample (healthy/broken) in UI.
2. Frontend calls `/api/signal/test?label=broken` → Signalgenerator generates signal data.
3. Signal sent to `/api/extract` → Featureextractor computes features.
4. Features to `/api/predict` → Faultclassifier predicts fault.
5. Results stored in MongoDB and displayed in UI.

## Troubleshooting
- **404 Errors**: Check Ingress rules in `k8s/ingress.yaml`.
- **Image Pull Errors**: Ensure images are pushed to registry.
- **Metrics Unavailable**: Verify Metrics Server with `kubectl top pods`.
- **Pods Not Scaling**: Check `kubectl describe hpa <name>` for CPU targets.

## Contributing
- Fork the repo.
- Create feature branch.
- Submit PR with tests.

## License
MIT License.

See [security.md](security.md) for security notes and [video-demo.md](video-demo.md) for demo walkthrough.
