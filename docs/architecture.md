# GearboxGuard Architecture

GearboxGuard is a microservices-based application designed for gearbox fault diagnosis using machine learning. It follows a modular, scalable architecture deployed on Kubernetes, with services communicating via HTTP APIs and data persisted in MongoDB. The system supports end-to-end signal simulation, feature extraction, fault classification, and user interaction through a web frontend.

## High-Level Overview
The architecture is event-driven and stateless (except for MongoDB), enabling horizontal scaling. Key principles:
- **Microservices**: Each service handles a specific concern (signal generation, extraction, classification, UI).
- **Containerization**: Docker images for each service.
- **Orchestration**: Kubernetes for deployment, scaling, and service discovery.
- **API Gateway**: NGINX Ingress for routing and load balancing.
- **Data Store**: MongoDB for storing raw signals, extracted features, and predictions.
- **Scaling**: Horizontal Pod Autoscalers (HPAs) based on CPU utilization.

### Component Diagram (Text-Based)
```
[User Browser] --> [NGINX Ingress (Port 80)] --> [Frontend Service (Port 80)]
                                                                 |
                                                                 v
[API Calls: /api/signal/test] --> [Signalgenerator Service (Port 8000)] --> MongoDB (Signals Collection)
                                                                 |
[API Calls: /api/extract] --> [Featureextractor Service (Port 8100)] --> MongoDB (Features Collection)
                                                                 |
[API Calls: /api/predict] --> [Faultclassifier Service (Port 8001)] --> MongoDB (Predictions Collection)
                                                                 |
                                                                 v
[Results] <-- [Frontend] <-- [Ingress]
```

## Components

### 1. **Frontend (React/Static HTML + Nginx)**
   - **Purpose**: User interface for selecting samples (healthy/broken), displaying signal plots, and showing predictions.
   - **Tech**: HTML/CSS/JS, served by Nginx in Docker.
   - **Deployment**: Kubernetes Deployment (1 replica default), Service (ClusterIP), HPA (min 2, max 10).
   - **Resources**: CPU request 100m/limit 500m, Memory 128Mi/512Mi.
   - **Files**: `frontend/index.html`, `frontend/styles.css`, `frontend/Dockerfile`, `k8s/deployments/frontend-deployment.yaml`.

### 2. **Signalgenerator (FastAPI/Python)**
   - **Purpose**: Generates synthetic vibration signals based on label (healthy/broken) using NumPy/SciPy.
   - **Endpoints**: GET `/test?label={healthy|broken}` → Returns JSON array of signal data.
   - **Tech**: FastAPI, NumPy, SciPy, PyMongo for storing signals.
   - **Deployment**: Kubernetes Deployment (1 replica), Service (ClusterIP), HPA (min 2, max 10).
   - **Resources**: CPU 200m/1000m, Memory 256Mi/1Gi.
   - **Files**: `signalgenerator/app/main.py`, `signalgenerator/requirements.txt`, `k8s/deployments/signalgenerator-deployment.yaml`.

### 3. **Featureextractor (FastAPI/Python)**
   - **Purpose**: Extracts features (e.g., RMS, kurtosis, FFT peaks) from raw signals.
   - **Endpoints**: POST `/` → Accepts signal data, returns feature vector JSON.
   - **Tech**: FastAPI, SciPy for signal processing, PyMongo.
   - **Deployment**: Kubernetes Deployment (1 replica), Service (ClusterIP), HPA (min 2, max 10).
   - **Resources**: CPU 300m/1500m, Memory 512Mi/2Gi.
   - **Files**: `featureextractor/app/main.py`, `featureextractor/app/extractor.py`, `requirements.txt`, `k8s/deployments/featureextractor-deployment.yaml`.

### 4. **Faultclassifier (FastAPI/Python)**
   - **Purpose**: Loads trained ML model (e.g., Random Forest) to classify features as healthy or broken.
   - **Endpoints**: POST `/` → Accepts features, returns prediction (e.g., {"fault": "broken", "confidence": 0.95}).
   - **Tech**: FastAPI, scikit-learn for model, PyMongo for logging predictions.
   - **Deployment**: Kubernetes Deployment (1 replica), Service (ClusterIP), HPA (min 2, max 10).
   - **Resources**: CPU 500m/2000m, Memory 1Gi/4Gi (higher for ML inference).
   - **Files**: `faultclassifier/app/main.py`, `faultclassifier/app/classifier.py`, `requirements.txt`, `k8s/deployments/faultclassifier-deployment.yaml`.

### 5. **MongoDB (Stateful Database)**
   - **Purpose**: Persistent storage for test signals (`test_signals`), features (`features`), and predictions (`predictions`).
   - **Tech**: Official MongoDB Docker image (v7).
   - **Deployment**: Kubernetes Deployment (1 replica; use StatefulSet for production), Service (ClusterIP), PersistentVolumeClaim.
   - **Secrets**: `mongodb-secret` for MONGO_URI.
   - **Collections**: `gearbox.test_signals_broken`, `gearbox.predictions`.
   - **Files**: `k8s/deployments/mongodb-deployment.yaml`, `k8s/services/mongodb-service.yaml`, `k8s/secrets.yaml`.

### 6. **NGINX Ingress Controller**
   - **Purpose**: Routes external traffic to services with path rewriting (e.g., `/api/signal/test` → signalgenerator `/test`).
   - **Config**: Regex paths with `nginx.ingress.kubernetes.io/rewrite-target: /$2`.
   - **Deployment**: Installed via Helm or manifests (assumed in cluster).
   - **Files**: `k8s/ingress.yaml`.

### 7. **Supporting K8s Resources**
   - **Services**: ClusterIP for internal communication.
   - **ConfigMaps/Secrets**: `k8s/configmap.yaml`, `k8s/secrets.yaml` for env vars.
   - **HPAs**: CPU-based autoscaling (`k8s/hpa-*.yaml`).
   - **PVC**: For MongoDB persistence (`k8s/deployments/mongodb-pvc.yaml`).

## Data Flow
1. **User Input**: Frontend sends GET to Ingress `/api/signal/test?label=broken`.
2. **Routing**: Ingress rewrites to signalgenerator `/test` → Generates signal → Stores in MongoDB → Returns data.
3. **Extraction**: Frontend POSTs signal to `/api/extract` → Rewritten to featureextractor `/` → Extracts features → Stores → Returns vector.
4. **Prediction**: POST features to `/api/predict` → Rewritten to faultclassifier `/` → Predicts → Stores prediction → Returns result.
5. **UI Update**: Frontend plots signal and displays prediction.

## Deployment and Scaling
- **Apply All**: `kubectl apply -f k8s/`.
- **Manual Scale**: `kubectl scale deployment <service> --replicas=<n>`.
- **Auto Scale**: HPAs trigger on CPU >70%; Metrics Server required.
- **Monitoring**: `kubectl top pods/nodes`, `kubectl get hpa`.

## Tech Stack
- **Backend**: Python 3.10+, FastAPI, NumPy, SciPy, scikit-learn, PyMongo.
- **Frontend**: HTML/JS/CSS, Plotly.js for charts.
- **Infra**: Docker, Kubernetes, NGINX Ingress, MongoDB.
- **ML Model**: Trained on gearbox fault datasets (e.g., broken30hz.csv); loaded via joblib.

For security considerations, see [security.md](security.md). For a demo walkthrough, see [video-demo.md](video-demo.md).
