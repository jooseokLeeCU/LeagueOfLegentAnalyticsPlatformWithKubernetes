VERSION=v1
DOCKERUSER=seungwooklee

build:
	docker build -f Dockerfile -t final-worker2 .

push:
	docker tag final-worker2 $(DOCKERUSER)/final-worker2:$(VERSION)
	docker push $(DOCKERUSER)/final-worker2:$(VERSION)
	docker tag final-worker2 $(DOCKERUSER)/final-worker2:latest
	docker push $(DOCKERUSER)/final-worker2:latest