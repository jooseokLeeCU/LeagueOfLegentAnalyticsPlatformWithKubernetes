VERSION=v1.1
DOCKERUSER=seungwooklee

build:
	docker build -f Dockerfile -t backup .

push:
	docker tag backup $(DOCKERUSER)/backup:$(VERSION)
	docker push $(DOCKERUSER)/backup:$(VERSION)
	docker tag backup $(DOCKERUSER)/backup:latest
	docker push $(DOCKERUSER)/backup:latest