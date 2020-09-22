# epic-games-interview

## Table of Contents

1. [Question 1](#question-1)
    1. [Approach](#approach)
    2. [Usage Example](#usage-example)
    3. [Terraform](#terraform)
    4. [Assumptions](#assumptions)
    5. [Duration](#duration)
    6. [Prerequisites](#prerequisites)
    7. [How to test](#how-to-test)
    8. [Cleanup](#cleanup)
    9. [Nice to haves](#nice-to-haves)
2. [Question 2](#question-2)
3. [Question 3](#question-3)
4. [Question 4](#question-4)

## Question 1

### Approach

Firstly, thank you all for the opportunity to interview with Epic Games. I love challenges and this project exposed me to a tech stack I have never worked with. Regardless of the outcome of my interview, I am glad to have the experience that came from this project.

To solve this problem I used Python 3. Since I wanted a script that pulled metrics (rather than an agent that pushes), I went with executing `ps aux` over SSH to give me the memory stats. I used the [paramiko](http://www.paramiko.org/) package to easily connect/execute commands remotely via Python. I also used python [statsd](https://github.com/jsocol/pystatsd) module as a client wrapper for interacting with statsd.

To satisfy the parallel processing requirement of this assessment I went with Python 3's built-in `multiprocessing`. I used the `starmap()` function on 8 pooled workers for most of the script's functions.

The execution workflow looks like this:

1. User input is collected via `argparse`
2. A class `MemCollector()` is initialized with `get_mem_metrics_multi()` function
3. `get_mem_metrics_multi()` creates a pool of 8 workers and simultaneously executes the following
4. Using `paramiko` it connects to N number remote hosts via SSH to execute a `ps aux` command
5. The results are then sent to `send_to_statsd()` which parses and structures them further
6. It uses the `statsd.StatsClient().pipeline()` function to build a payload of multiple gauge metrics to cut down on network overhead
7. It is sent to `statsd` on UDP 8125 to the host you specify on step 1

I arrived at this solution, because I did not want the complexity of deploying agents on hosts and have them periodically send metrics. This one script can aggregate all the process memory usage and send it to statsd/graphite easily.

### Usage Example

Hosts you want to monitor

```text
8.8.8.8
1.1.1.1
127.0.0.1
```

Graphite(statsd) host

```text
13.28.0.5
```

The command would be:

```bash
./mem_collector.py -u <ssh_username> -k <your_private_key>.pem -i 8.8.8.8,1.1.1.1,127.0.0.1 -g 13.28.0.5
```

### Terraform

For my integration tests and development workflow I chose to go with terraform to bring up my infrastructure in AWS. While it is not required for you to do this, it tests parallel processing time over remote networks pretty well.

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

**NOTE** You must have an AWS account and keypair with EC2 and VPC full access for this to work. You will also be spinning up AWS resources which will incur charges to your AWS account. You are responsible for any charges due to AWS resources running in your account. To make sure everything is cleaned up use `terraform destroy`.

1. Use `make init` to generate your python virtual environment as well as a private key to use for testing.

2. Activate your virtual environment via `source bin/activate`

3. Install the python package dependencies with `make install_deps`

4. Build and run a docker container to test metric gathering/processing with `make test`

5. (OPTIONAL) Deploy terraform for a remote test using `make deploy`. You will need to wait approximately 5min for the graphite install to be finished. You can check if it is done by going to the graphite url output with `terraform output`

6. (OPTIONAL) Run `make remote_test` to test on your EC2 instances and graphite.

### Cleanup

To clean up, run `make clean_all`. Then `deactivate` to leave your python virtual env.

### Nice to haves

* Better documented code. Python in most cases is pretty straightforward to read, but it would have been nice to document the code better and describe classes, functions, and returns better.

* Better logging with timestamps and more accurate exceptions.

* Better unit tests in place with mock data. All of my tests were integration.

* CI/CD system to deploy terraform. I would use GitHub actions + [Atlantis](https://www.runatlantis.io/) to achieve this.

* CI/CD system to test the python script. I have never used [Tox](https://tox.readthedocs.io/en/latest/), but that looks like a good way to go.

* Give the choice to use a SSH port rather than TCP 22. This would be easy to implement, but I did not for the sake of time.

* Prebake an EC2 AMI with synthesize stack, so it doesn't take so long to bootstrap

## Question 2

If I had to run this multi-region and scaled to 10,000 hosts I would ask myself the following:

### How will Graphite keep up with the load?

From what I have [read](https://allegro.tech/2015/09/scaling-graphite.html) putting multiple carbon-relays behind a load balancer would be a good call. I would also make sure the hardware of the graphite servers was adequate via performance testing. From what I gather, it appears disk IO (due to whisper) and RAM are the most important resources to tune. I would also look into sharding metrics between regions to reduce network latency and disk IO wait due to whisper being overloaded. Replacing as many Python components of Graphite [with Go](https://github.com/go-graphite) also appears to provide a large improvement.

### How can I run my script more efficiently?

I would need to run some benchmarks on my script to see how many hosts/metrics can be gathered in a reasonable amount of time. For the definition of a "reasonable time" let's say that is below one minute. This will give us the opportunity to get minute resolution metrics if needed. Then I would need to figure out a method of autodiscovering these hosts.

If our infrastructure mainly in AWS I could use I would first see if AWS Lambda is a good fit for executing the script.
This is where the pull methodology of my solution falls flat. It would be far more simple to distribute an agent to all these hosts that periodically pushes their metrics to their region's graphite load balancer.

### Am I making this easily scalable for more than 10,000 hosts?

I'll go back to my previous statement about the pull vs push collection. I think by making this script an agent it would scale to N hosts rather easily. I would make the script a python package that could be easily installed via `pip`.

### Duration

This question took me approximately: 1 hour

## Question 3

I would use DataDog to monitor the `statsd` service on the graphite hosts and PagerDuty to send me alerts. I would create a monitor on DataDog for the `statsd` [service](https://docs.datadoghq.com/integrations/systemd/?tab=host#overview). I would check for `systemd.unit.active` on `statsd`. If ever gets in a not active state an alert will trigger and be forwarded to PagerDuty. I would also do a synthetic test by sending a gauge to a specific path in graphite every N minutes. I could then have another script that pulls that gauge and checks the last timestamp it was reported. If the gauge has not been reporting in for a predetermined amount of time it would trigger a PagerDuty alert. I would do this for every graphite host that has `statsd`.

If I was not able to use DataDog or PagerDuty I would go with the tried and true bash script, cron, and email. I could also modernize things a bit by incorporating a webhook into Slack instead of just email.

### Duration

This question took me approximately: 30 minutes

## Question 4

The way I typically approach monitoring and alerting on oom killer events is first starting with what hosts are running out of memory. In the past I have set up Icinga2 to run its memory check scripts on remote hosts and report back the free memory %. If their memory usage is outside of normal bounds, I would be alerted and further investigation would take place.

In my experience the easiest way to drill down on OOM killer issues is via system logs. Assuming I was permitted to use DataDog, I would use DataDog logs with a [log filter](https://www.datadoghq.com/blog/diagnosing-oom-errors-with-datadog/#collect-oom-logs-from-your-system) for oom killer events. If I wasn't able to use DataDog, I would put together `rsyslog` and a central syslog server. There I would have a bash script that would alert on oom killer events see in the logs.

To further investigate I would identify the process/pid(s) that are consuming the most amount of memory. That is where this project's script would shine. There could be a few causes to general high memory usage. There might be load balancing issues, so I would check connections via `lsof` if it is a part of a backend cluster. It's also possible there is too much disk pressure and the scheduler cannot flush data in memory to disk fast enough. However, after investigating all of that the host may need to be vertically scaled with additional RAM.

Once I have identified the process I would SSH to one of the 1% hosts. SSH connections and pttys usually take priority with oom killer, so I will most likely get on. If not I would have to unfortunately "turn it off and on again". I would look at the application or system level logs to see if there are any clues as to why the process is consuming more memory each hour.

Since this issue is occurring every hour regularly it might be a garbage collection issue (java). If that's the case an immediate band aid would be a cron job that restarts the java service every X minutes. Obviously this is a 3am patch solution, so we need to investigate the application more to find a proper solution.

### Duration

This question took me approximately: 1 hour
