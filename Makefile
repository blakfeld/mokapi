container_name ?= blakfeld/mokapi
version ?= $(shell awk -F' = ' '{print $$2 }'  mokapi/__version__.py | sed s"/'//g")

###
# Building
###
build:
	@docker build \
		--tag "$(container_name):latest" \
		--tag "$(container_name):$(version)" \
		.

###
# Run
###
run:
	@docker run --rm \
		--publish 8000:8000 \
		--volume "$(spec_file)":/tmp/spec.yaml \
		"$(container_name):$(version)" \
		/tmp/spec.yaml