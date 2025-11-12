.PHONY: docker-build-push-dev docker-build-push-prod run-gvirtus-backend-dev run-gvirtus-tests stop-gvirtus docker-build-openpose run-openpose-test stop-openpose-test

docker-build-push-dev:
	docker buildx build \
		--platform linux/amd64 \
		--push \
		--no-cache \
		-f docker/dev/Dockerfile \
		-t taslanidis/gvirtus-dependencies:cuda12.6.3-cudnn-ubuntu22.04 \
		.

docker-build-push-prod:
	docker buildx build \
		--platform linux/amd64 \
		--push \
		--no-cache \
		-f docker/prod/Dockerfile \
		-t taslanidis/gvirtus:cuda12.6.3-cudnn-ubuntu22.04 \
		.

run-gvirtus-backend-dev:
	docker run \
		--rm \
		-it \
		--network host \
		--gpus all \
		-v ./cmake:/gvirtus/cmake/ \
		-v ./etc:/gvirtus/etc/ \
		-v ./include:/gvirtus/include/ \
		-v ./plugins:/gvirtus/plugins/ \
		-v ./src:/gvirtus/src/ \
		-v ./tools:/gvirtus/tools/ \
		-v ./tests:/gvirtus/tests/ \
		-v ./CMakeLists.txt:/gvirtus/CMakeLists.txt \
		-v ./docker/dev/entrypoint.sh:/entrypoint.sh \
		-v ./examples:/gvirtus/examples/ \
		--entrypoint /entrypoint.sh \
		--name gvirtus \
		--shm-size=8G \
		taslanidis/gvirtus-dependencies:cuda12.6.3-cudnn-ubuntu22.04

attach-gvirtus-bash:
		docker exec -it gvirtus bash

run-gvirtus-tests:
	docker exec \
		-it gvirtus \
		bash -c \
		'export LD_LIBRARY_PATH=$$GVIRTUS_HOME/lib/frontend:$$LD_LIBRARY_PATH && \
			cd /gvirtus/build && \
			ctest --output-on-failure'

stop-gvirtus:
	docker stop gvirtus


docker-build-openpose:
	docker buildx build \
		--platform linux/amd64 \
		--push \
		--no-cache \
		-f examples/openpose/Dockerfile \
		-t darsh916/openpose_gvirtus:cuda12.6 \
		examples/openpose	


#run-openpose-test: 
#	docker run --rm \
#		--name openpose_test_container \
#		--network host \
#		-v ./examples/openpose/media:/opt/openpose/examples/media \
#		-v ./examples/openpose:/opt/openpose/examples/gvirtus \
#		-v ./examples/openpose/properties.json:/opt/GVirtuS/etc/properties.json \
#		-v ./examples/openpose/entrypoint.sh:/entrypoint.sh \
#		darsh916/openpose_gvirtus:cuda12.6 \
#		bash /entrypoint.sh --image_path=$(INPUT_FILE)

# Docker   
run-openpose-test: 
	docker run --rm \
		--name openpose_test_container \
		--network host \
		-v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/examples/openpose/media:/opt/openpose/examples/media \
		-v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/examples/openpose:/opt/openpose/examples/gvirtus \
		-v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/examples/openpose/properties.json:/opt/GVirtuS/etc/properties.json \
		-v /home/cldemo/guaitolini/virtual_mirror_GVirtus/GVirtuS/examples/openpose/entrypoint.sh:/entrypoint.sh \
		darsh916/openpose_gvirtus:cuda12.6 \
		bash /entrypoint.sh --image_path=$(INPUT_FILE)

stop-openpose-test:
	docker stop openpose_test_container || true