# Instructions/Notes

* State your assumptions when you solve each problem.
* All code is run through a test suite to test its production quality; these tests affect whether or not our interview process continues, so please take them seriously.
* Please try to give an approximate time that it took you to solve each portion of the exercise.
* Be aware that there may be multiple ways to solve some of the questions.
* We’d also like to request that you keep the answers to these questions private.  If you post them to a web link, github account etc. please do your best to make them private.  

## Question 1

Write a script in bash, ruby, python or golang that in parallel would collect per process used memory across 50 linux hosts.  The collected information should be output to a suitable metrics back-end via statsd(TICK, prometheus, statsite)  If you are not sure what this is, then please use https://github.com/obfuscurity/synthesize. Please do not use an agent such as telegraf or collectd.  We would like to see how you would code this :)

## Question 2

Given the same scenario in question 1, what would you change or consider if you needed to run this across 10,000 hosts across multiple regions?  Please describe this in detail including how you would architect and scale metrics collection and services.

## Question 3

Given the same scenario from question 2,  how do you know the statsd service is working correctly?  What monitoring or metrics would you put in place if this was a production service?  Please talk about specific architectures and systems you would use for this monitoring tool.  Gotchas are an a+.

## Question 4

If 1% of hosts(out of 10k total) were kernel OOMing every hour(with linux OOMkiller kicking in), what action would you take to auto remediate? How would you discover and monitor that the hosts were in fact running out of memory?
