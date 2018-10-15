# Mokapi

Pronounced Mo-Kapi because we all love cutesy names :D

We use the Open API specification (Version 3) to design RESTful APIs. I'm a big fan of this, as Open API
specification gives you a lot of bang for your buck (documentation, generated code, etc), but I've found that an API
that is well designed on paper isn't always any fun to actually _use_. The purpose of this tool is to slurp in an Open
API Spec (Version 3) and to generate a mock server with mocked data so you can query around and see if the models and
paths you've defined are actually pleasant to use and reason about.

This tool currently only supports GET operations with JSON return values (as that's what I'm mostly concerned with at
this moment) return values, but it could easily be extended to cover whatever is needed (Pull requests welcome!). When
performing a GET on a path configured in the provided Open API Spec, **Mokapi** will search the provided spec for a
route that matches that request, it will read through the configured response, and do it's best to create a mock version
of that response, and return it. It will also search through any configured query parameters, and allow you to use those
as filters. Any query params that are not configured will be ignored.

## Docker Usage

Just run it from docker hub:

```bash
$ docker run --rm \
	--publish 8000:8000 \
	--volume /my/totally/rad/spec.yml:/tmp/spec.yaml \
	"utils/mokapi" \
	/tmp/spec.yaml
```

## Script Usage

Just execute it as a python module:

```bash
$ python mokapi my/totally/rad/spec.yml
```


## Building and Running Locally

I've provided handy Makefile targets that should do what you need:

```bash
$ make build  # build docker container locally
$ make run spec_file=/my/totally/rad/spec.yml
```

