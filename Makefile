# ---------------------------
# Variables
export PYTHONPATH := $(shell pwd)/src
APP_NAME=music_app
IMAGE_NAME=$(APP_NAME):latest
CONTAINER_NAME=$(APP_NAME)_container
PORT=8001
PYTHON=python3.12
VENV=venv

.DEFAULT_GOAL := help
# Help target: displays all available commands and descriptions in a table
help:
	@echo "+------------------+--------------------------------------------+"
	@echo "| Command          | Description                                |"
	@echo "+------------------+--------------------------------------------+"
	@echo "| venv             | Create virtual environment                 |"
	@echo "| install          | Install python requirements                |"
	@echo "| run-locally      | Run app locally                            |"
	@echo "| clean-venv       | Remove the virtual environment             |"
	@echo "| docker-build     | Build the docker image                     |"
	@echo "| docker-run       | Run the docker container                   |"
	@echo "| docker-stop      | Stop the docker container                  |"
	@echo "| docker-remove    | Remove the docker container                |"
	@echo "| docker-logs      | View the logs of the running docker cont.  |"
	@echo "| docker-shell     | Open a shell inside the docker container   |"
	@echo "| docker-clean     | Stop and remove the docker container       |"
	@echo "| docker-remove-img| Remove the docker image                    |"
	@echo "+------------------+--------------------------------------------+"

venv: 
	$(PYTHON) -m venv $(VENV)

install: venv
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

run_locally:
	PYTHONPATH=src cd src && ../$(VENV)/bin/uvicorn main:app --reload

clean-venv:
	rm -rf $(VENV)

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run -d --name $(CONTAINER_NAME) -p $(PORT):8001 $(IMAGE_NAME)

docker-stop:
	docker stop $(CONTAINER_NAME)

docker-remove:
	docker rm $(CONTAINER_NAME)

docker-logs:
	docker logs -f $(CONTAINER_NAME)

docker-shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

docker-clean: docker-stop docker-remove

docker-remove-image:
	docker rmi $(IMAGE_NAME)