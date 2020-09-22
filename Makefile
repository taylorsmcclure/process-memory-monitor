## Makefile for this project. You can use this to test things before using remote CI/CD.

.PHONY: clean_all

all:

# Setup your dev environment and launch your docker compose cluster
init: virtual_env gen_ssh_key
	terraform init
	@echo
	@echo Python virtual env created. Use source bin/activate to start developing.

gen_ssh_key:
	./gen_key.sh

virtual_env:
	python3 -m venv .

install_deps:
	pip3 install -r requirements.txt

clean_all: docker_compose_down
	terraform destroy
	rm -rf bin/ include/ lib/ .terraform/ terraform.tfstate* epic-interview.pem epic-interview.pub
	docker rmi epic-memory-test:latest
	@echo run deactivate to get our of your python venv

clean_docker: docker_compose_down
	docker stop epic-memory-test; docker rm epic-memory-test; docker rmi epic-memory-test

deploy:
	terraform init
	terraform validate
	terraform fmt
	@echo "This will deploy resources to your AWS account. This will incure charges to your account. Are you sure you want to deploy this? [y/N] " && read ans && [ $${ans:-N} = y ]
	terraform apply

docker_compose_up: gen_ssh_key
	docker-compose up -d

docker_compose_down:
	docker-compose down

build_container: gen_ssh_key
	docker build -t epic-memory-test:latest .

run_container:
	docker run -d -p 22:22 --rm --name epic-memory-test epic-memory-test:latest

test: docker_compose_up
	./mem_collector.py -u root -k epic-interview.pem -i localhost -g localhost -o
	./tests/check_localhost_output.py

remote_test:
	@read -p "Enter public IP for your remote instance(s):" instance_ip; \
	./mem_collector.py -u ubuntu -k epic-interview.pem -i $$instance_ip -g localhost -o
	./tests/check_localhost_output.py
