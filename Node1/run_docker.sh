# 0) Start back-end service for GVirtus
ssh $USER_BACK@$IP_BACK 'export BACK_DIR=$HOME/guaitolini/virtual_mirror_GVirtus
                        pkill -f "$BACK_DIR/bin/gvirtus-backend"; \
                        export GVIRTUS_HOME=$BACK_DIR/GVirtuS; \
                        export LD_LIBRARY_PATH="$GVIRTUS_HOME/lib:$LD_LIBRARY_PATH"; \
                        nohup $GVIRTUS_HOME/bin/gvirtus-backend $GVIRTUS_HOME/etc/properties.json > $GVIRTUS_HOME/gvirtus.log 2>&1 &'

# 1) Close previous iterations.
docker stop smart-mirror && docker rm smart-mirror

# 2) Run docker
docker run -it \
  --name smart-mirror \
  --network host \
  -v /home/cldemo/.ssh:/root/.ssh:ro \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /home/cldemo/guaitolini/virtual_mirror_GVirtus/shared-data-tmp/:/app/shared-data-tmp \
  -v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/:/app/GVirtuS \
  -v /home/cldemo/guaitolini/virtual_mirror_GVirtus/RDMA_functions/:/app/RDMA_functions \
  -p 3000:3000 -p 5000:5000 -p 8000:8000 \
  smart-mirror



#  -v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/examples/openpose/media:/app/media \
