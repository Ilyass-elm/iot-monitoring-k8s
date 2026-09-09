# IoT Monitoring Lab

In this project, I built an IoT application to live-monitor sensor data. I have simulated a temperature sensor using an MQTT client that is sending data every 2 seconds. When the data arrives at the broker, it gets pulled by 2 clients:

- Telegraf: It is an open source agent used to write and aggregate data. I used it to map incoming data to a timeseries database (influxDB). This can be e.g. used to set alarms when a treshhold is reached or to train a machine learning model in the future.
  
- Backend: has a built-in dataStore element that stores the last few hundreds data points and hands them to the frontend. 

![alt text](https://github.com/Ilyass-elm/iot-monitoring-k8s/blob/main/iot-schema.png)

All services run in a Kubernetes cluster and communicate through the internal DNS service provided by Kuberenetes. 

# Initial Setup

Before you start building the application, you need to install and set up the development environment for K8s. For this project, the following tools are required: **Docker, minikube, and kubectl**.

### 1. Docker

The official guide to install and set up Docker on a Linux machine can be found [here](https://docs.docker.com/engine/install/ubuntu/).

### 2. kubectl

`kubectl` is the command-line tool used to interact with a Kubernetes cluster. To install it, run the following two commands:

```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### 3. Minikube

`kubectl` needs access to a Kubernetes API Server in order to communicate with and manage a cluster. In this demo, I will use **minikube** to create and run a local Kubernetes cluster.

To install minikube, run the following commands:

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

Check if the installation was successful:

```bash
minikube version
```

### 4. Cluster

Change the directory to `iot-monitoring-k8s` and start the minikube cluster:

```bash
minikube start
```

**Note:** Minikube needs to be started again whenever the computer is restarted. Simply run:

```bash
minikube start
```
If you want minikube to start automatically whenever your machine is turned on, follow this [tutorial](https://joepreludian.medium.com/how-to-start-up-minikube-automatically-via-system-d-2cad99fd79bf).


Since I'm using ingress, this should be enabled in minikube. To do this, run the following command:

```bash
minikube addons enable ingress
```

The Ingress Controller is optional. Its main purpose is to forward requests from outside the cluster to internal applications, for example, if you want to access the dashboard. Normally, applications running inside a cluster are not directly accessible from outside. An Ingress provides a way to route external HTTP/HTTPS requests to internal services.

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
kubectl apply -f src/dashboard/
```

Run the following command to check if all pods are running. If the status of any pod is showing something else than running, run the second command, go to the bottom and take a look at the **Events** section.
```bash
kubectl get pods -n iot-monitoring
# If any pods is not running, run:
kubectl describe pod <POD-NAME> -n iot-monitoring
```

To access the dashboard, copy the IP Address shown when running the following command:
```bash
kubectl get ingress ingress -n iot-monitoring
```
Now open `/etc/hosts` and modify it as shown below:
```
<IP-ADDRESS>  iot-dashboard.com  influxdb.iot-dashboard.com
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

### Ingress
This is very relevant when running websites or applications on a Kuberenetes cluster if external requests are expected. Ingress helps to map them to the right service, keeping all other ones hidden and safe. 

### Multiple-Container Pod
The dashboard deployment contains 2 containers: frontend and backend. This makes the internal communication between the 2 containers easier without any further configruation. Inside a pod, alle containers can be reached from other containers with no constrains or extra configuration. Putting one of the containers in a seperate pod would require adding a LoadBalancer, which is in this case not necessary. 

### Furthering K8s Understanding

This is a hands-on project that demonstrates the role of different K8s objects, such as Services and Deployments. I also had the opportunity to use a **StatefulSet** for the InfluxDB component to persist data, which is a common pattern when running stateful applications in Kubernetes.
