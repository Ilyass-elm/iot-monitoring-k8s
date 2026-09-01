# IoT Monitoring Lab

In this project, I built an IoT application to live-monitor sensor data. All services run in a Kubernetes (hereafter **K8s**) cluster and communicate through the internal DNS service provided by K8s.

# Initial Setup

Before we start building the application, we need to install and set up the development environment for K8s. For this project, the following tools are required: **Docker, kind, and kubectl**. A Docker Hub account is also required, where the created Docker images will be pushed.

### 1. Docker

The official guide to install and set up Docker on a Linux machine can be found [here](https://docs.docker.com/engine/install/ubuntu/).

### 2. kubectl

`kubectl` is the command-line tool used to interact with a Kubernetes cluster. To install it, run the following two commands:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### 3. API Server for K8s

`kubectl` needs access to a Kubernetes API Server in order to communicate with and manage a cluster. In this demo, I will use **kind** to create a local Kubernetes cluster.

To install it, run the following commands:

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

Check if the installation was successful:

```bash
kind version
```

### 4. Cluster

Change the directory to `iot-monitoring-k8s` and run the following command:

```bash
kind create cluster --name iot-stack --config kind-config.yaml
```

The Ingress Controller is optional. Its main purpose is to forward requests from outside the cluster to internal applications, for example, if you want to access a dashboard that is running in a pod. Normally, applications running inside a cluster are not directly accessible from outside. An Ingress provides a way to route external HTTP/HTTPS requests to internal services.

Note that in production environments, exposing applications to the outside should generally be secured using TLS.

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=120s
```

After that, create a namespace to keep all the application components organized in one place:

```bash
kubectl create namespace iot-monitoring
```

# Build the Services

Run the following command to start the MQTT broker:

```bash
kubectl apply -k src/iot-broker/
```

To check if the pod is running, run:

```bash
kubectl get pods -n iot-monitoring -w
```

You might initially see `ContainerCreating` under the status. Give it a few seconds and it should change to `Running`. If it takes too long or shows a different status, go back and check whether all the previous steps were completed correctly.

Afterwards, build the rest of the application components one by one. Always check after deploying a component that the corresponding pod is running.

```bash
kubectl apply -f src/database/

# Pay attention here: -k and NOT -f.
# More details in the Lessons Learned section.
kubectl apply -k src/elegraf/

kubectl apply -f src/publisher/
kubectl apply -f src/backend/
kubectl apply -f src/frontend/
```

# Lessons Learned

### Debugging

While building this application, I ran into many issues, including pods not running and some naming mismatches. One of the commands that I used frequently when facing an issue was:

```bash
kubectl describe pod PODNAME -n iot-monitoring
```

Here, you can see relevant information about the pod, including its state, image, and the actions or events that have taken place, such as pulling the Docker image.

### Linking Configuration Files

I used `mosquitto.conf` and `telegraf.conf` to configure their respective services. In this case, there are two options: **Kustomize** and **ConfigMap**.

Kustomize is not primarily developed for this purpose, but I still wanted to test it. This is the reason why the `-k` flag is required whenever a `kustomization.yaml` file is inside a directory. It tells `kubectl` to process the Kustomize configuration in that directory, which can then generate the required Kubernetes resources, such as a ConfigMap.

Later on, I will rebuild the application and use ConfigMaps directly, without relying on Kustomize for this purpose. Check the other branches for updates.

### Furthering K8s Understanding

This is a hands-on project that demonstrates the role of different K8s objects, such as Services and Deployments. I also had the opportunity to use a **StatefulSet** for the InfluxDB component to persist data, which is a common pattern when running stateful applications in Kubernetes.

