# epic-games-interview

## Terraform

## Question 1

### Assumptions

* Each host we are collecting memory from are running Ubuntu 18.04 LTS. If this was going through a production readiness checklist, I would take inventory of all the hosts it will be deployed to, then create an end-to-end test running the collection script against them.

* The statsd collector will need to listen on udp 8125 and sync its data to graphite periodically. I used the [suggested stack](https://github.com/taylorsmcclure/synthesize).

* For the user to test the script the need an AWS account and IAM credentials that have EC2 and VPC access.

* The user running the script is on OS X. I did not test this with Windows 10. The Makefile and bash scripts may not work.

* User is connected to the internet/has a public IP address.

* All Linux hosts have a user with the same public key. This user will need access to run `ps aux`.

* "collect per process used memory". I am interrupting this as collecting virtual and resident memory alongside memory usage percent for each process using `ps aux`. They will be split into different metrics for each host/pid.

* I will not need to provide any custom grafana views to show the metrics.

* SSH connection (auth, wait) and remote exec timeouts are all set to 5 seconds. The script will continue collecting data after it exceeds that threshold.

* Sending metrics to the graphite server will timeout after 5 seconds and fail.

* I am permitted to use a statsd client library.

* I need to use a [fork of synthesize](https://github.com/taylorsmcclure/synthesize) from a previous interview candidate (haha). I also [increased some carbon metrics](https://github.com/taylorsmcclure/synthesize/commit/1f01414e58155dee59b40d8769c503a039fc1bf5) CRUDs per second and minute so no metrics drop.

* I will not need to worry about a lifecycle policy for the data in graphite.

* I am tracking memory using the command's name, then drilling down to a pid

### Duration

This question took me approximately: 

### How to test

**NOTE** You must have an AWS account and keypair with EC2 and VPC full access for this to work. You will also be spinning up AWS resources which will incure charges to your AWS account. You are responsible for any charges due to AWS resources running in your account. To make sure everything is cleaned up use `terraform destroy`.

1. Use `make deploy` to create your test infrastructure. This will launch...

### Nice to haves

* Better documented code. Python in most cases is pretty straightforward to read, but it would have been nice to document the code better and describe classes, functions, and returns better.

* Better logging with timestamps and more accurate exceptions.