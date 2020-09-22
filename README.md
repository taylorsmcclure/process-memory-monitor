# epic-games-interview

## Table of Contents

[Question 1](#question-1)
    - [Approach](#approach)
    - [Terraform](#terraform)
    - [Assumptions](#assumptions)
    - [Duration](#duration)
    - [Prerequisites](#prerequisites)
    - [How to test](#how-to-test)
    - [Cleanup](#cleanup)
    - [Nice to haves](#nice-to-haves)

## Question 1

### Approach

...

### Terraform

For my integration tests and development I chose to go with terraform to bring up my infrastructure in AWS. While it is not required for you to do this, it tests parallel processing time over remote networks pretty well.

### Assumptions

* Each host we are collecting memory from are running Ubuntu 18.04 LTS. If this was going through a production readiness checklist, I would take inventory of all the hosts it will be deployed to, then create an end-to-end test running the collection script against them.

* The statsd collector will need to listen on udp 8125 and sync its data to graphite periodically. I used the [suggested stack](https://github.com/taylorsmcclure/synthesize) with some minor tweaks on my fork.

* For the user to test the script the need an AWS account and IAM credentials that have EC2 and VPC access.

* The user running the script is on OS X. I did not test this with Windows 10. The Makefile and bash scripts may not work.

* User is connected to the internet/has a public IP address.

* All Linux hosts have a user with the same public key. This user will need access to run `ps aux`.

* "collect per process used memory". I am interpreting this as collecting virtual and resident memory for each process using `ps aux`. They metrics will be stored in the following convention `host.command.pid*`.

* I will not need to provide any custom grafana views to show the metrics.

* SSH connection (auth, wait) and remote exec timeouts are all set to 5 seconds. The script will continue collecting data on subsequent hosts.

* Sending metrics to the statsd server will timeout after 5 seconds and fail. Having a connection error reaching the remote statsd instance will result in the script exiting.

* I am permitted to use a statsd client library. I used [this](https://github.com/jsocol/pystatsd).

* I will not need to worry about a lifecycle policy for the data in graphite.

* I am tracking memory using the command's name, then drilling down to a pid, which is then split to rss and vss.

### Duration

This question took me approximately: 8 hours

### Prerequisites

* Docker with Docker Compose

* Able to have the docker container listen on TCP 22 locally

* (OPTIONAL) If you want to test remotely on AWS EC2, you will need IAM credentials that has full access to EC2 and VPC.
  * You also need `terraform` v0.12 installed

### How to test

**NOTE** You must have an AWS account and keypair with EC2 and VPC full access for this to work. You will also be spinning up AWS resources which will incure charges to your AWS account. You are responsible for any charges due to AWS resources running in your account. To make sure everything is cleaned up use `terraform destroy`.

1. Use `make init` to generate your python virtual environment as well as a private key to use for testing.

2. Activate your virtual environment via `source bin/activate`

3. Install the python package dependencies with `make install_deps`

4. Build and run a docker container to test metric gathering/processing with `make test`

5. (OPTIONAL) Deploy terraform for a remote test using `make deploy`. You will need to wait approximately 5min for the graphite install to be finished. You can check if it is done by going to the graphite url output with `terraform output`

6. (OPTIONAL) Run `make remote_test` to test on your EC2 instances and graphite.

### Cleanup

To clean up run `make clean_all`. Then `deactivate` to leave your python virtual env.

### Nice to haves

* Better documented code. Python in most cases is pretty straightforward to read, but it would have been nice to document the code better and describe classes, functions, and returns better.

* Better logging with timestamps and more accurate exceptions.

* Better unit tests in place with mock data. All of my tests were integration.

* CI/CD system to deploy terraform. I would use GitHub actions + [Atlantis](https://www.runatlantis.io/) to achieve this.

* CI/CD system to test the python script. I have never used [Tox](https://tox.readthedocs.io/en/latest/), but that looks like a good way to go.

* Use an SSH port rather than TCP 22. This would be easy to implement, but I did not for the sake of time.

* Prebake an EC2 AMI with synthesize stack, so it doesn't take so long to bootstrap

## Question 2