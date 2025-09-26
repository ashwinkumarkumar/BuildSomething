# GearboxGuard Security

GearboxGuard prioritizes security in its microservices architecture, focusing on data protection, access control, and secure deployment practices. As a diagnostic tool handling simulated industrial data, it follows best practices for Kubernetes and API security. Below are key security considerations and implementations.

## 1. **Secrets Management**
- **MongoDB Credentials**: Sensitive data like `MONGO_URI` is stored in Kubernetes Secrets (`k8s/secrets.yaml`). Avoid hardcoding in YAMLs or code.
  - Creation: `kubectl create secret generic mongodb-secret --from-literal=mongo-uri="mongodb://user:pass@host:port/db"`.
  - Usage: Referenced in Deployments via `valueFrom.secretKeyRef`.
- **Best Practice**: Use external secret managers like HashiCorp Vault or AWS Secrets Manager for production. Rotate secrets regularly.

## 2. **API Security**
- **Authentication/Authorization**: Currently unauthenticated (for demo). In production:
  - Add JWT tokens via FastAPI dependencies in services (signalgenerator, featureextractor, faultclassifier).
  - Use OAuth2 with Keycloak or Auth0 for user login in frontend.
- **Rate Limiting**: Implement in FastAPI with `slowapi` to prevent DDoS (e.g., limit requests per IP).
- **Input Validation**: All endpoints use Pydantic models for schema validation to prevent injection attacks.
- **HTTPS**: Enforce TLS on Ingress (`k8s/ingress.yaml`) with cert-manager for Let's Encrypt certificates.
  - Annotation: `kubernetes.io/ingress.class: nginx`, `cert-manager.io/cluster-issuer: letsencrypt-prod`.

## 3. **Network Security**
- **Ingress Rules**: NGINX Ingress restricts paths (e.g., `/api/*` only). Use NetworkPolicies to isolate services:
  - Example NetworkPolicy YAML for frontend to only allow traffic from Ingress:
    ```yaml
    apiVersion: networking.k8s.io/v1
    kind: NetworkPolicy
    metadata:
      name: frontend-allow-ingress
    spec:
      podSelector:
        matchLabels:
          app: frontend
      ingress:
      - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
    ```
  - Apply: `kubectl apply -f k8s/networkpolicies/`.
- **Service Isolation**: Services use ClusterIP (internal only); no external exposure except via Ingress.

## 4. **Data Protection**
- **MongoDB**: 
  - Enable authentication in Deployment env vars.
  - Use TLS for connections (add `ssl=true` to MONGO_URI).
  - Backup: Configure PersistentVolume with encryption (e.g., AWS EBS encryption).
- **Sensitive Data**: No real user data; simulated signals only. In production, anonymize industrial data.
- **Compliance**: Aligns with GDPR/SOC2 basics (data minimization, access logs).

## 5. **Container and Deployment Security**
- **Image Scanning**: Scan Docker images with Trivy or Clair before pushing (e.g., `trivy image ashwin0302/frontend:latest`).
- **Pod Security Standards**: Enforce via PodSecurityPolicies or Admission Controllers (e.g., runAsNonRoot: true in Deployments).
- **Resource Limits**: Set in Deployments to prevent DoS from rogue pods (already implemented: CPU/Memory limits).
- **RBAC**: Use least-privilege roles; default service accounts are sufficient for demo.

## 6. **Monitoring and Auditing**
- **Logs**: Services log to stdout (captured by Kubernetes). Use ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging.
- **Auditing**: Enable Kubernetes audit logs; track API calls in services.
- **Vulnerability Management**: Regular updates to dependencies (e.g., `pip check` for Python).

## 7. **Potential Risks and Mitigations**
- **Risk**: Unsecured MongoDB exposure → Mitigation: Secrets + NetworkPolicies.
- **Risk**: API abuse → Mitigation: Rate limiting + auth.
- **Risk**: Image vulnerabilities → Mitigation: Scan and use minimal base images (e.g., python:3.10-slim).
- **Risk**: Scaling overload → Mitigation: HPA max replicas + resource quotas.

For production, conduct a full security audit (e.g., with OWASP ZAP for APIs). Report issues to maintainers.

See [architecture.md](architecture.md) for component details and [README.md](../README.md) for setup.
