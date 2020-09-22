# epic-games-interview

## Terraform

## Question 1

### Assumptions

* Each host we are collecting memory from are running Ubuntu 18.04 LTS. If this was going through a production readiness checklist, I would take inventory of all the hosts it will be deployed to, then create an end-to-end test running the collection script against them.

* The statsd collector will need to listen on udp 8125 and sync its data to graphite periodically. I used the [suggested stack](https://github.com/taylorsmcclure/synthesize) with some minor tweaks on my fork.

* For the user to test the script the need an AWS account and IAM credentials that have EC2 and VPC access.

* The user running the script is on OS X. I did not test this with Windows 10. The Makefile and bash scripts may not work.

* User is connected to the internet/has a public IP address.

* All Linux hosts have a user with the same public key. This user will need access to run `ps aux`.

* "collect per process used memory". I am interrupting this as collecting virtual and resident memory for each process using `ps aux`. They metrics will be stored in the following convention `host.command.pid`.

* I will not need to provide any custom grafana views to show the metrics.

* SSH connection (auth, wait) and remote exec timeouts are all set to 5 seconds. The script will continue collecting data on subsequent hosts.

* Sending metrics to the statsd server will timeout after 5 seconds and fail. Having a connection error reaching the remote statsd instance will result in the script exiting.

* I am permitted to use a statsd client library. I used [this](https://github.com/jsocol/pystatsd).

* I need to use a [fork of synthesize](https://github.com/taylorsmcclure/synthesize) from a previous interview candidate (haha). I also [increased some carbon metrics](https://github.com/taylorsmcclure/synthesize/commit/1f01414e58155dee59b40d8769c503a039fc1bf5) CRUDs per second and minute so no metrics drop.

* I will not need to worry about a lifecycle policy for the data in graphite.

* I am tracking memory using the command's name, then drilling down to a pid, which is then split to rss and vss.

### Duration

This question took me approximately: 

### Prerequisites to test

* Docker with Docker Compose

* Able to have the docker container listen on TCP 22 locally

### How to test

**NOTE** You must have an AWS account and keypair with EC2 and VPC full access for this to work. You will also be spinning up AWS resources which will incure charges to your AWS account. You are responsible for any charges due to AWS resources running in your account. To make sure everything is cleaned up use `terraform destroy`.

1. Use `make deploy` to create your test infrastructure. This will launch...

### Nice to haves

* Better documented code. Python in most cases is pretty straightforward to read, but it would have been nice to document the code better and describe classes, functions, and returns better.

* Better logging with timestamps and more accurate exceptions.

* Better unit tests in place with mock data. All of my tests were integration.

* CI/CD system to deploy terraform. I would use GitHub actions + [Atlantis](https://www.runatlantis.io/) to achieve this.

* CI/CD system to test the python script. I have never used [Tox](https://tox.readthedocs.io/en/latest/), but that looks like a good way to go.

* Use an SSH port rather than TCP 22. This would be easy to implement, but I did not for the sake of time.
