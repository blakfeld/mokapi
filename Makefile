container_name ?= utils/mokapi
ecr_repo ?= "143242038773.dkr.ecr.us-east-1.amazonaws.com"
version ?= $(shell awk -F' = ' '{print $$2 }'  mokapi/__version__.py | sed s"/'//g")

###
# Building
###
build:
	@docker build \
		--tag "$(container_name):latest" \
		--tag "$(container_name):$(version)" \
		.

push:
	@docker tag "$(container_name):$(version)" "$(ecr_repo)/$(container_name):$(version)"
	@docker push "$(ecr_repo)/$(container_name):$(version)"

build-and-push: build push

###
# Run
###
run:
	@docker run --rm \
		--publish 8000:8000 \
		--volume "$(spec_file)":/tmp/spec.yaml \
		"$(container_name):$(version)" \
		/tmp/spec.yaml