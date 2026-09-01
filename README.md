# IoT Monitoring lab

In this project I built an IoT application to live monitor sensor data. All services run in a Kubernetes (in following k8s) cluster und communicate through the internal DNS-Service of k8s.

# Initial Setup
before we start writing a single configuration file, we need to install and setup the development environment for k8s. For this Project the following tools are needed: docker, kind, and kubectl. A docker hub account is also required, where the crrated docker images will be pushed. 
### 1. Docker
The official link to install and setup docker on a linux machine is [here](https://docs.docker.com/engine/install/ubuntu/).
### 2. kubectl
This is the tool for .... To install, run the following 2 commands:
```curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```
### 3. API Server for K8S
kubectl needs an API Server in order to create a cluster locally. In this demo I will use **kind**.
To install it, run the following commands:
```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```
Check if the installation has been successfull:
```
kind version
```
### 4. Cluster 
change directory to iot-monitoring-k8s and run the following commands:

```
kind create cluster --name iot-stack --config kind-config.yaml
```
The Ingress Controller is optional. Its main purpose is to forward requests from the outside into the internal application ,e.g. if you want to see a dashboard that's running in a pod. Normally you cannot access it as it is totally isolated in the locall clsuter. Ingress makes it possible to open a communication port with internal services. Note that in production this almost always the case, however you must set TLS for security. More on this topic later on this guide.
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
kubectl -n ingress-nginx wait --for=condition=Ready pod -l app.kubernetes.io/component=controller --timeout=120s
```
After that create a namespace to keep all the created components organized in one space:
```
kubectl create namespace iot-monitoring
```
### 5. Build the services 
Run the following the command to start the MQTT-broker:
```
kubectl apply -k src/iot-broker/
```
To check if the pod is running, run:
```
kubectl get pods -n iot-monitoring -w
```
You might see under status "ContainerCreating", just give some seconds and it will be running. If it takes too long or shows other status than running, go back and check if you run all the previous steps correctly.
Afterwords build the rest of the application components one by one. Always check after deploying a component if the pod is running.
```
kubectl apply -f src/database/
kubectl apply -k src/elegraf/
kubectl apply -f src/publisher/
kubectl apply -f src/backend/
kubectl apply -f src/frontend/
```
