VERSION=v3.1
DOCKERUSER=seungwooklee

build:
	docker build -f Dockerfile -t final-worker .

push:
	docker tag final-worker $(DOCKERUSER)/final-worker:$(VERSION)
	docker push $(DOCKERUSER)/final-worker:$(VERSION)
	docker tag final-worker $(DOCKERUSER)/final-worker:latest
	docker push $(DOCKERUSER)/final-worker:latest
