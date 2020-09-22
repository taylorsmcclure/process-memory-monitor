## Makefile for this project. You can use this to test things before using remote CI/CD.

.PHONY: clean_all

all:

# Setup your dev environment and launch your docker compose cluster
init: virtual_env
	terraform init
	@echo
	@echo Python virtual env created. Use source bin/activate to start developing.
	./gen_key.sh

virtual_env:
	python3 -m venv .

install_deps:
	pip3 install -r requirements.txt

clean_all:
	terraform destroy
	rm -rf bin/ include/ lib/ .terraform/ terraform.tfstate* epic-interview.pem epic-interview.pub
	@echo run deactivate to get our of your python venv

deploy:
	terraform init
	terraform validate
	terraform fmt
	@echo "This will deploy resources to your AWS account. This will incure charges to your account. Are you sure you want to deploy this? [y/N] " && read ans && [ $${ans:-N} = y ]
	terraform apply