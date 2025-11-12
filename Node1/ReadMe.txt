# ---------------------------------------------------------------------------------------
# VIRTUAL MIRROR WEB APPLICATION
#
#
# 11, 2025 - Michelangelo Guaitolini
# ---------------------------------------------------------------------------------------

This is to detail the components of the Virtual Mirror Web Application developed for the
CLEVER project. The application is designed to capture a picture of the user, process it
and then use processed data to combine the original picture with a garment chosen by the
user.
The applicaton is deployed through two servers: the front-end one is dedicated to run the 
web application and pre-processing operations and the back-end server is dedicated to run
VITON service. 
The front-end server is provided with CPU only, while the second comprises a GPU, which
will allow for faster processing. The GPU on the back-end server is also accessible by
the front-end through the GVirtus service. 

# ---------------------------------------------------------------------------------------
0 - Configuration.
    Environmental parameters, such as ip addresses and filepaths, are defined in
    "env_config.json".

    To deploy the application in a new environment, please change this file accordingly 
    before launch.
    
# ---------------------------------------------------------------------------------------
1 - THE WEB APPLICATION
    You may run the web application through ./run_web_app_build.sh

    This will start all the services that are necessary to interact with the application
    through https link. It will also start the GVirtus back-end portion on the back-end
    server: this will be necessary to use the GVirtus service during pre-processing
    operations.
    
    The web application may require you to confirm you want to access the ip address and
    to work properly it is necessary to confirm that you want to proceed also on :5000,
    since otherwise a portion of the application will be blocked.
    
    The web application comprises 2 web pages: "Home", and "Demo". "Home" is for basic
    application and upload pictures, "Demo" is for the version with the webcam.
    It will require you to give the application access to your webcam, then you will be
    allowed to take pictures, process them and virtually try clothes.
    
    For what concerns the underlying code, the web application files are under the 
    /web_app:
      - front-end: under /viton directory.
                  - "Demo" page is detaied in "New.jsx"
                  
      - back-end : app.py, this file contains everything to run the application and its
                           functions.; 
                   live.py;
    
    When an image is capture it is stored in a temporary directory with a unique_id 
    automatically generated. You may find this directory under /shared-data-tmp/. Any 
    further processing and result will regard operations on this directory.
    
# ---------------------------------------------------------------------------------------
2 - PRE-PROCESS
    Image processing is performed by the ./parallel_process.sh script.
    
    It executes, in parallel, openpose and 2D-Human-Parsing. 
    - 2D-Human-Parsing
    - Openpose: openpose is executed leveraging on GVirtus (virtual GPU) service. To
                do so, it will leverage on custom scripts available at 
                - /GVirtuS/examples/openpose/.
    
    The script waits until both processes are complete, then it sends the unique_id 
    directory to the back-end for VITON service. In terms of latency, the two portions
    perform as it follows: 
    
    - 2D-Human-Parsing: ~6 seconds.
    - Openpose (with GVirtus): ~15 seconds. 
    
    Openpose is taking too much time and should be optimized further.
    
# ---------------------------------------------------------------------------------------
3 - RDMA Transfer
    Data transfer between the two servers exploits RDMA communication, and is executed via
    ./rdma_service.sh. 
    The scrip initializes a new rdma call any time a transfer is needed and the directory
    needs to be zipped and then unzipped to be transferred as the channel is able to 
    transfer files, not directories. There are probably better ways to use it. Must be 
    optimized.
    
    RDMA-related scripts, both for client and server services, are detailed under 
    /RDMA_functions.
    
# ---------------------------------------------------------------------------------------
4 - VITON-HD
    VITON application is executed on the back-end server. When processed data reach the 
    back-end the user is presented with a catalogue of garments to try on. Selecting a 
    cloth and launching the application will generate the result image.
    To be shown to the user, the result image is transferred to the front-end, using rdma
    transfer.
    
    VITON process is executed launching ./run_only_viton.sh and it takes ~12 seconds to 
    provide a result.
    Users may try multiple garments just running the associated commands on the web 
    applications, without the need to go through image processing again.
    
    
    