# GearboxGuard

## Overview

GearboxGuard is a comprehensive microservices-based application designed for fault diagnosis in gearboxes using machine learning techniques. It simulates synthetic vibration signals for healthy and faulty (broken) gearboxes, extracts relevant features from these signals, classifies potential faults using a pre-trained ML model, and provides an interactive web frontend for users to test and visualize results. The system is built with scalability in mind, leveraging Docker for containerization and Kubernetes for orchestration, with MongoDB as the persistent data store.

This project was developed to demonstrate an end-to-end ML pipeline for predictive maintenance in industrial applications, specifically targeting gearbox health monitoring. It uses vibration data inspired by real-world datasets (e.g., from the Case Western Reserve University bearing fault dataset, adapted for gearboxes).

## Key Features

- **Signal Generation**: Synthetic vibration signals generated using NumPy and SciPy to mimic healthy or broken gearbox behavior at 30Hz sampling rate.
- **Feature Extraction**: Computes time-domain (RMS, kurtosis) and frequency-domain (FFT peaks) features from signals.
- **Fault Classification**: Uses a pre-trained Random Forest model (from scikit-learn) to predict if the gearbox is healthy or faulty, with confidence scores.
- **Web Frontend**: Simple HTML/JS interface with Plotly.js for plotting signals and displaying predictions.
- **Data Persistence**: MongoDB stores raw signals, extracted features, and predictions for logging and analysis.
- **Scalability**: Kubernetes deployments with Horizontal Pod Autoscalers (HPAs) for auto-scaling based on CPU usage.
- **Local Development**: Docker Compose for easy local setup and testing.

## Tech Stack

- **Backend Services**: Python 3.10+, FastAPI (for APIs), NumPy, SciPy (signal processing), scikit-learn (ML), PyMongo (DB interactions).
- **Frontend**: HTML5, CSS3, JavaScript, Plotly.js (for interactive charts), served via Nginx.
- **Database**: MongoDB 7.x.
- **Containerization**: Docker (Dockerfiles for each service).
- **Orchestration**: Kubernetes (deployments, services, ingress, configmaps, secrets, HPAs).
- **API Routing**: NGINX Ingress Controller for path-based routing.
- **Development Tools**: Jupyter Notebooks (for model training), Git for version control.

## Project Structure

```
gearboxGuard/
├── .env                  # Environment variables (e.g., MONGO_URI)
├── .gitignore            # Git ignore patterns (add sensitive files here)
├── README.md             # This file
├── docker-compose.yml    # Local development with Docker Compose
├── data/                 # Sample datasets (broken30hz.csv, healthy30hz.csv)
├── docs/                 # Documentation
│   ├── README.md         # Project docs overview
│   ├── architecture.md   # Detailed architecture
│   └── security.md       # Security considerations
├── frontend/             # Web UI
│   ├── index.html        # Main page with JS for API calls and plotting
│   ├── styles.css        # Styling
│   ├── nginx.conf        # Nginx config for serving static files
│   └── Dockerfile        # Builds Nginx image
├── signalgenerator/      # Service to generate signals
│   ├── app/
│   │   ├── main.py       # FastAPI app with /test endpoint
│   │   └── simulator.py  # Signal simulation logic
│   ├── requirements.txt  # Python deps (FastAPI, NumPy, SciPy, PyMongo)
│   └── Dockerfile        # Builds Python image
├── featureextractor/     # Service for feature extraction
│   ├── app/
│   │   ├── main.py       # FastAPI app with / endpoint (POST signal)
│   │   ├── extractor.py  # Feature extraction functions
│   │   └── utils.py      # Helper utilities
│   ├── requirements.txt
│   └── Dockerfile
├── faultclassifier/      # ML classification service
│   ├── app/
│   │   ├── main.py       # FastAPI app with / endpoint (POST features)
│   │   ├── classifier.py # Model loading and prediction
│   │   ├── models.py     # ML model definitions
│   │   ├── db.py         # MongoDB interactions
│   │   └── model.pkl     # Pre-trained Random Forest model
│   ├── requirements.txt  # Includes scikit-learn
│   └── Dockerfile
├── k8s/                  # Kubernetes manifests
│   ├── configmap.yaml    # Shared configs
│   ├── secrets.yaml      # Sensitive data (e.g., DB creds)
│   ├── ingress.yaml      # NGINX Ingress routing
│   ├── deployments/      # Pod deployments for each service + MongoDB
│   ├── services/         # ClusterIP services
│   └── hpa-*.yaml        # Autoscalers for services
└── gearboxGuard/         # (Legacy/backup dir, can be ignored)
```

## How It Was Made: Detailed Development Process

### 1. **Data Preparation and Model Training**
   - **Dataset Source**: Started with the "gearbox-fault-diagnosis-elaborated-datasets" dataset, containing raw CSV files like `broken30hz.csv` and `healthy30hz.csv`. These represent vibration signals at 30Hz for faulty and normal gearboxes.
   - **Preprocessing**: Used Jupyter Notebook (`TrainingModel.ipynb`) to load CSVs, add noise (Gaussian std dev variations: 10, 100, 1000), compute features (RMS, peak-to-peak, kurtosis, skewness, FFT coefficients), and label data (0: healthy, 1: broken).
   - **Model Training**: Split data (80/20 train/test), trained a Random Forest Classifier (n_estimators=100, max_depth=10) on features. Achieved ~95% accuracy on test set. Saved model as `model.pkl` using joblib.
   - **Why Random Forest?**: Ensemble method robust to noisy industrial data; interpretable feature importances (e.g., kurtosis most important for fault detection).
   - **Files Involved**: `data/*.csv`, `TrainingModel.ipynb`, `faultclassifier/app/model.pkl`.

### 2. **Microservices Design**
   - **Modular Approach**: Broke the pipeline into independent services for scalability. Each service is a FastAPI app exposing REST endpoints, communicating via HTTP (no direct DB access except for logging).
   - **Signalgenerator**:
     - Generates 1024-sample signals using sine waves + noise. For broken: adds harmonics (e.g., 2x/3x fundamental frequency to simulate gear mesh faults).
     - Stores generated signal in MongoDB (`test_signals` collection) with timestamp and label.
     - Built iteratively: Started with simple NumPy sin wave, added SciPy for realistic modulation.
   - **Featureextractor**:
     - Takes signal array, computes 10+ features (e.g., `rms = np.sqrt(np.mean(signal**2))`, FFT via `scipy.fft`).
     - Stores features in MongoDB (`features` collection).
     - Development: Tested features in notebook, ported to utils.py for reuse.
   - **Faultclassifier**:
     - Loads `model.pkl`, predicts on feature vector: `clf.predict_proba(features.reshape(1, -1))`.
     - Returns JSON: `{"fault": "broken", "confidence": 0.95}`. Logs prediction to MongoDB (`predictions`).
     - Trained model exported from notebook; inference optimized for low latency.
   - **Communication**: Services depend on MongoDB; frontend calls via API paths (e.g., `/api/signal/test`).

### 3. **Frontend Development**
   - **Simple SPA**: `index.html` loads JS to fetch signals (GET), extract features (POST), predict (POST), then plots with Plotly (time-series for signal, bar for prediction).
   - **API Integration**: Uses Fetch API; e.g., `fetch('/api/signal/test?label=broken').then(res => res.json())`.
   - **Styling**: Basic CSS for layout; responsive design for plots.
   - **Nginx**: Serves static files, proxies API calls (but in K8s, Ingress handles routing).
   - **Iteration**: Started with static plots, added interactivity (buttons for healthy/broken).

### 4. **Containerization with Docker**
   - **Each Service**: Custom Dockerfile (e.g., `FROM python:3.10-slim`, `COPY . /app`, `pip install -r requirements.txt`, `CMD ["uvicorn", "app.main:app"]`).
   - **Frontend**: `FROM nginx:alpine`, copy static files, custom `nginx.conf` for SPA routing.
   - **MongoDB**: Official image with volume for persistence.
   - **Testing Locally**: `docker-compose up` starts all services; access frontend at `localhost:8081`.
   - **Build Process**: Multi-stage for Python (no dev deps in prod); optimized layers.

### 5. **Kubernetes Orchestration**
   - **Why K8s?**: For production scalability, service discovery, and zero-downtime updates.
   - **Deployments**: One per service (replicas=1 default), with resource requests/limits (e.g., faultclassifier needs more CPU for ML).
   - **Services**: ClusterIP for internal; Ingress for external (rules: `/api/signal/(.*)` → signalgenerator, rewrite target).
   - **Storage**: PVC for MongoDB data (`mongodb-pvc.yaml`).
   - **Config/Secrets**: ConfigMap for non-sensitive (e.g., API ports), Secrets for DB URI (base64 encoded).
   - **Scaling**: HPAs target 70% CPU threshold, min=2/max=10 pods per service.
   - **Development**: Wrote YAML manifests iteratively; tested with `minikube` or local cluster. Applied via `kubectl apply -f k8s/`.
   - **Ingress Setup**: Assumes NGINX Ingress installed; annotations for path rewriting.

### 6. **Database Integration**
   - **Schema**: Collections like `gearbox.test_signals` (docs: {signal: array, label: str, timestamp: date}), similar for features/predictions.
   - **PyMongo**: Each service connects via `MONGO_URI` from env; inserts on success.
   - **Why MongoDB?**: Flexible schema for varying signal lengths; JSON-like docs match API responses.

### 7. **Testing and Iteration**
   - **Unit Tests**: Basic (e.g., pytest for feature extraction accuracy).
   - **End-to-End**: Local docker-compose, then K8s dry-run (`kubectl apply --dry-run`).
   - **Challenges Overcome**:
     - Signal realism: Tuned noise levels based on dataset stdev files.
     - ML Accuracy: Feature selection via notebook ablation studies.
     - K8s Routing: Debugged Ingress rewrites with `kubectl logs`.
     - Performance: Optimized FFT computations for real-time.
   - **Datasets**: Copied raw CSVs to `data/`; generated stdev variants in notebook.

## Quick Start (Local)

1. **Prerequisites**: Docker, Docker Compose installed.
2. **Clone Repo**: `git clone https://github.com/ashwinkumarkumar/BuildSomething.git && cd gearboxGuard`
3. **Env Setup**: Copy `.env.example` to `.env` and set `MONGO_URI=mongodb://localhost:27018/gearbox` (adjust port).
4. **Run**: `docker-compose up -d` (builds and starts services).
5. **Access**: Open `http://localhost:8081` in browser. Select "Healthy" or "Broken", click "Generate & Predict" to see signal plot and fault prediction.
6. **View DB**: Connect to MongoDB at `localhost:27018` to query collections.

## Production Deployment (Kubernetes)

1. **Cluster Setup**: Minikube, EKS, or GKE with Metrics Server (for HPAs).
2. **Secrets**: Update `k8s/secrets.yaml` with real DB creds.
3. **Apply**: `kubectl apply -f k8s/` (order: configmap/secrets → pvc → deployments → services → hpa → ingress).
4. **Ingress**: Expose via LoadBalancer or NodePort; access at `<ingress-ip>/`.
5. **Scale**: `kubectl scale deployment frontend --replicas=3`.
6. **Monitor**: `kubectl get pods/services/hpa`, `kubectl logs <pod-name>`.

## Troubleshooting

- **Docker Build Fails**: Check requirements.txt for version conflicts (e.g., `pip install --no-cache-dir`).
- **K8s Pods Crash**: Inspect logs; common: missing Secrets or PVC bind issues.
- **API Errors**: Verify MONGO_URI; test endpoints with `curl` (e.g., `curl http://localhost:8000/test?label=healthy`).
- **Model Issues**: Retrain if accuracy drops; update `model.pkl`.

## Contributing

- Fork the repo, create a feature branch (`git checkout -b feature/new-feature`).
- Commit changes (`git commit -m 'Add new feature'`).
- Push and open PR to `main`.

## License

MIT License. See LICENSE file (add if needed).

For more details, see [docs/architecture.md](docs/architecture.md) and [docs/security.md](docs/security.md).

---

*Project built by Aswin Kumar as part of ML/DevOps exploration.*
