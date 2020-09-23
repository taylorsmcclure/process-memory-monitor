#!/usr/bin/env python
from multiprocessing import Pool
from itertools import repeat
import paramiko
import statsd

# color formatting for console messages
# https://stackoverflow.com/a/287944
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MemCollector ():
    def __init__(self, output=False):
        self.output = output

    def get_mem_metrics_single(self, hostnames, key_file, user, graphite_host):
        for h in hostnames:
            self.get_mem_metrics(h, key_file, user, graphite_host)

    def get_mem_metrics_multi(self, hostnames, key_file, user, graphite_host):
        with Pool() as p:
            p.starmap(self.get_mem_metrics, list(zip(hostnames, repeat(key_file), repeat(user), repeat(graphite_host))))

    def send_to_statsd(self, graphite_host, results, host):
        host = "{}".format(host.replace('.', '-'))
        
        # This usually won't fail since UDP, but nice to have
        with statsd.StatsClient(host=graphite_host, port=8125, prefix="memory_usage", maxudpsize=512).pipeline() as p:
            if self.output:
                with open('metrics.log', 'w') as f:
                    f.seek(0)
                    f.write(str(results))
            
            for r in results:
                r = r.split(' ')
                command = r[0]
                pid = r[1]
                path = "{}.{}.{}".format(host, command, pid)
                p.gauge("{}.rss".format(path), float(r[2]))
                p.gauge("{}.vss".format(path), float(r[3]))

        # This usually won't fail since UDP, but nice to have
        try:
            p.send()
        except Exception as e:
            print("{}FAIL: {}. Cannot push metrics to statsite {}:8125{}".format(bcolors.FAIL, e, graphite_host, bcolors.ENDC))
            raise(e)

        print("{}INFO: memory metrics sent to statsite server {}:8125{}".format(bcolors.OKGREEN, graphite_host, bcolors.ENDC))        
        return True

    def get_mem_metrics(self, hostname, key_file, user, graphite_host):
        # load your private key
        pkey = paramiko.rsakey.RSAKey.from_private_key_file(key_file)
        # initiate SSH connection to host
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # command to gather mem metrics
        command = 'sudo ps ax -o comm,pid,rss,vsz | grep -v \'grep\|ps\|tail\|sed\' | tail -n +2 | sed -re \'s,\s+, ,g\''
        try:
            client.connect(hostname, username=user, allow_agent=False,
            look_for_keys=False, pkey=pkey, timeout=5, auth_timeout=5, banner_timeout=5)
        except Exception as e:
            print("{}FAIL: {} for host {}\nContinuing to next host.{}".format(bcolors.FAIL, e, hostname, bcolors.ENDC))
            return False

        print("{}INFO: SSH connection successful on {}{}".format(bcolors.OKGREEN, hostname, bcolors.ENDC))

        try:
            _, stdout, _ = client.exec_command(command, timeout=5)
        except Exception as e:
            print("{}FAIL: {} for host {}\nContinuing to next host.{}".format(bcolors.FAIL, e, hostname, bcolors.ENDC))
            return False

        print("{}INFO: Remote ps aux command successfully ran on {}{}".format(bcolors.OKGREEN, hostname, bcolors.ENDC))        

        results = stdout.readlines()
        client.close()
        # strip new line chars
        results = [line.rstrip() for line in results]
        self.send_to_statsd(graphite_host, results, hostname)
