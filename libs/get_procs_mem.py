#!/usr/bin/env python
from multiprocessing import Pool
from itertools import repeat
import paramiko
import time
import pickle
import struct
import socket
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
    def __init__(self):
        pass

    def get_mem_metrics_single(self, hostnames, key_file, user, graphite_host):
        for h in hostnames:
            self.get_mem_metrics(h, key_file, user, graphite_host)

    def get_mem_metrics_multi(self, hostnames, key_file, user, graphite_host):
        with Pool(8) as p:
            p.starmap(self.get_mem_metrics, list(zip(hostnames, repeat(key_file), repeat(user), repeat(graphite_host))))

    def send_to_statsd(self, graphite_host, results, host):
        host = "{}".format(host.replace('.', '-'))
        
        # This usually won't fail since UDP, but nice to have
        with statsd.StatsClient(host=graphite_host, port=8125, prefix="memory_usage", maxudpsize=512).pipeline() as p:
            for r in results:
                r = r.split(' ')
                command = r[0]
                pid = r[1]
                path = "{}.{}.{}".format(host, command, pid)
                print("{}.rss".format(path), float(r[2]))
                p.gauge("{}.rss".format(path), float(r[2]))
                print("{}.vss".format(path), float(r[3]))
                p.gauge("{}.vss".format(path), float(r[3]))
            
        # This usually won't fail since UDP, but nice to have
        try:
            p.send()
        except Exception as e:
            print("{}FAIL: {}. Cannot push metrics to statsite {}:8125{}".format(bcolors.FAIL, e, graphite_host, bcolors.ENDC))
            raise(e)

        print("{}INFO: memory metrics sent to statsite server {}:8125{}".format(bcolors.OKGREEN, graphite_host, bcolors.ENDC))        
        return True

    # pickles metrics to send to graphite
    # https://graphite.readthedocs.io/en/latest/feeding-carbon.html
    def pickle_metrics(self, host, results):
        graphite_root_path = "memory_usage.{}".format(host.replace('.', '-'))
        pickled_metrics = []
        unix_time = int(time.time())
        # I could probably be more efficient here
        for r in results:
            r = r.split(' ')
            path = "{}.{}".format(graphite_root_path, r[0])
            mem_percent = ("{}.mem_percent".format(path), (unix_time, r[1]))
            vss = ("{}.vss".format(path), (unix_time, r[2]))
            rss = ("{}.rss".format(path), (unix_time, r[3]))
            
            pickled_metrics.extend([mem_percent, vss, rss])

        payload = pickle.dumps(pickled_metrics, protocol=2)
        header = struct.pack("!L", len(payload))
        message = header + payload

        # print(pickled_metrics)
        return message

    def send_pickled_metrics(self, graphite_host, message):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((graphite_host, 2004))
        except Exception as e:
            print("{}FAIL: {}. Cannot push metrics to graphite on {}:2003{}".format(bcolors.FAIL, e, graphite_host, bcolors.ENDC))
            raise(e)

        s.sendall(message)
        print("{}INFO: memory metrics sent to graphite server {}{}".format(bcolors.OKGREEN, graphite_host, bcolors.ENDC))
        s.close()
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
        # print(results)
        
        # message = self.pickle_metrics(hostname, results)
        # self.send_pickled_metrics(graphite_host, message)

        self.send_to_statsd(graphite_host, results, hostname)

