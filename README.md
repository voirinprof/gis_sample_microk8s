# 🚀 Deploying a Flask + PostGIS + Nginx Application on MicroK8s

This project demonstrates how to deploy a full web application stack using **Flask**, **PostGIS**, and **Nginx** on a **MicroK8s** Kubernetes cluster.

## 📦 Stack Overview

- **Flask**: Python backend exposing a REST API.
- **PostGIS**: PostgreSQL database with geospatial extensions.
- **Nginx**: HTTP reverse proxy (used to expose the Flask API).
- **MicroK8s**: Lightweight Kubernetes distribution.

---

## 🔧 Requirements

- Ubuntu-based nodes (VMs or physical).
- [MicroK8s](https://microk8s.io/) installed on all nodes.
- Root/SSH access to each node.
- `kubectl` available (`microk8s kubectl` or alias).
- [Helm](https://helm.sh/) for optional deployments.

---

## 🧪 MicroK8s Setup

See [pythongeolab.com](https://pythongeolab.com/en/scalability/) for the installation

```bash
# On each node
sudo snap install microk8s --classic

# On the control plane node
microk8s add-node
```

Open the ports ```25000/tcp,16443/tcp,12379/tcp,10250/tcp,10255/tcp,10257/tcp,10259/tcp``` on the principal node.

Open the ports ```25000/tcp,10250/tcp,10255/tcp,19001/tcp``` on each node.


### Enable required addons

```bash
microk8s enable dns ingress storage helm dashboard
```

---

## 📁 Repository Structure

```
.
├── app/ # Flask application source code
│ └── main.py
├── helm/
│ ├── flask-app/ # Helm chart for Flask
│ ├── nginx/ # Helm chart for Nginx reverse proxy
│ └── postgis/ # Helm chart for PostGIS
├── README.md
```

---

## 🚀 Deployment Steps

### 1. Build & push your Docker images

You can either use local image registries or push to Docker Hub:


```bash
docker build -t my-flask-app:latest .
docker save my-flask-app:latest | microk8s ctr image import -
```

or

```bash
docker build -t youruser/flask-app:latest ./app
docker push youruser/flask-app:latest
```

Update the image references in `helm/flask-app/values.yaml`.

---

### 2. Deploy PostGIS

```bash
microk8s helm3 install postgis-release postgis/
```

> 🗺️ You can configure DB credentials and volumes via `helm/postgis/values.yaml`.

---

### 3. Deploy the Flask Application

```bash
microk8s helm3 install flask-release flask-app/
```

> Flask should be configured to connect to the PostGIS service via Kubernetes DNS (e.g., `postgis-db.default.svc.cluster.local`).

---

### 4. Deploy Nginx (Reverse Proxy)

```bash
microk8s helm3 install nginx-release nginx/
```

This will expose your app using an Ingress or LoadBalancer depending on your config.

---

## 🌐 Accessing the Application

Once deployed, retrieve the LoadBalancer IP:

```bash
microk8s kubectl get svc -A
```

Then test the Flask endpoint (proxied through Nginx):

```bash
curl http://<LOADBALANCER_IP>/status
```

---

## 🛠 Helm Chart Customization

Each chart under `helm/` has its own `values.yaml` for configuration:

* **`helm/flask-app/values.yaml`**: image name, port, env vars (DB, debug mode)
* **`helm/postgis/values.yaml`**: DB name, user, password
* **`helm/nginx/values.yaml`**: proxy config, ingress rules

---

## 🧪 Troubleshooting

* Check service discovery:

  ```bash
  microk8s kubectl exec -it <pod-name> -- nslookup postgis-db
  ```

* View pod logs:

  ```bash
  microk8s kubectl logs <pod-name>
  ```

* DNS problems? Check `coredns` logs:

  ```bash
  microk8s kubectl logs -n kube-system -l k8s-app=kube-dns
  ```
