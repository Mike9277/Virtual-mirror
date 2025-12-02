# Virtual Mirror Distributed Web Service
This repository contains the source code and the docker images developed in the context of Use Case 4 of the CLEVER project. The application is a virtual mirror application, allowing the users to combine their own pictures, acquired through webcam, with selected garments, virtually trying them on. The application is developed as a distributed service, displaced between two edge nodes. 

## Node 1
Is dedicated to interacting with the user, collecting images and pre-processing them before combining users’ pictures with garments. Node 1 is allowed to be a CPU-only device, leveraging either on CPU or virtual GPU to run the application.

1. **Web application**
   
   enables the https web service that allows the users to upload their pictures, take snapshots with their own webcam and use the provided service.

2. **Pre-processing**
   
   is necessary to map the images, recognizing poses and body areas. It uses openpose and 2D human parsing services. Openpose has been optimized to exploit a GPU virtualization service, allowing Node 1 to use Node 2 hardware resources, specifically its GPU.

3. **RDMA**
   
   Provides low-latency communication between Node 1 and Node 2, allowing to distribute the computational load as needed without compromising the Quality of Service. RDMA communication has been tested with servers connected through two Nvidia BlueField-2, leveraging on DOCA.

## Node 2
Is where backend services are activated, both for rdma and gpu virtualization. These services are necessary to create communication channels between Node 1 and Node 2, are activated at startup and allow low-latency communication and hardware resources exploitation by the service deployed at Node 1. Node 2 must be equipped with a GPU, as it is necessary to execute VITON service and to allow Node 1 to access to the GPU virtualization service.

## VITON
This service is what merges images and garments and is deployed as an isolated container. In standard configuration is deployed on Node 2, but it may be deployed on Node 1 if local deployment is necessary.

## Environment Setting
1. **Download Node 1 and Node 2 directories**
   
   All the executable in this projects are designed to run inside containers but they expect a basic structure on the host and they need access to specific folders on the host. To be sure to have the correct setup on your directories, download Node1 repository on your Node1 and Node2 repository on Node2. Then, rename the two directories so that they have the same filepath (es. /home/username/virtual_mirror/), as the application expects that. At this point, you may pull the necessary images on your servers.

2. **Pull containers**
   
   Now, download the necessary docker containers.

   On Node 1:
   ```bash
   docker pull ghcr.io/mike9277/virtual_mirror_node_1:latest
   ```
   On Node 2:
   ```bash
   docker pull ghcr.io/mike9277/virtual_mirror_node_2:latest
   ```
   ```bash
   docker pull ghcr.io/mike9277/virtual_mirror_viton:latest
   ```
   If you want to test the local deployment you may want to pull virtual_mirror_viton docker also on Node 1.
   
4. **Config environment**
   
   Finally, you will need to edit **env_config.json** to set your own filepaths and addresses. This file sets all the environmental variables necessary to run the application and to allow communication between Node 1 and Node 2. 

## Set GPU Virtualization
The application leverages on GPU virtualization service provided by GVirtus. GVirtus is handled as an external service, and it needs its own setup procedure. The original repository, available at [Link text](https://github.com/ecn-aau/GVirtuS/tree/dev) has been modified to integrate it with the rest of the application. To properly setup GVirtus service, execute the following steps:

1. **Adjust server address **
   
   On Node 1, modify the ip address at .../GVirtuS/examples/openpose/properties.json, where "server_address" must be changed to your Node 2 ip address.
   ```bash
   {
     "communicator": [
       {
         "endpoint": {
           "suite": "tcp/ip",                   
           "protocol": "tcp",                     
           "server_address": "10.30.7.117",        
           "port": "8888"
         },
         "plugins": [
           "cuda",
           "cudart",
           "cublas",
           "curand",
           "cudnn",
           "cufft",
           "cusolver",
           "cusparse",
           "nvrtc"
         ]
       }
     ],
     "secure_application": false
   }
   ```
2. **Adjust Frontend (Node 1) Docker components**
   
   GVirtuS operates in a client-server model, where the fronted functions as the client and the backend serves as the GPU execution engine. It relies on docker components that need to be set before executing the service. On Node 1, execute the following steps:

   ```bash
   docker pull darsh916/gvirtus
   ```
   ```bash
   docker run --network host --privileged --name gvirtus_frontend -t gvirtus-env bash
   ```
3. **Adjust Backend (Node 2) Docker components**

   As said, Node 2 should be a GPU-enabled device. Before proceeding, ensure the following requirements are met: Nvidia drivers should be installed and nvidia-container-toolkti must be configured. Then, you need to execute the following steps:

   ```bash
   docker pull darsh916/gvirtus
   ```
   ```bash
   docker run --network host --privileged --name gvirtus_backend --gpus all -t gvirtus-env bash
   ```

Now that GVirtuS has been configured, you don't need to worry about anything else: it will be initialized and run at startup when the rest of the application is started.

## Run the application 
You may run the application on Node 1, with the following command:
```bash
./start_application.sh
```
