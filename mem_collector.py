#!/usr/bin/env python

import argparse
import datetime
from libs import get_procs_mem

parser = argparse.ArgumentParser()
   
parser.add_argument('-i', '--hostnames', dest='hostnames', help="(REQUIRED) comma sparated list hostnames to collect memory statistics", required=True)
parser.add_argument('-k', '--key', dest='p_key', help="(REQUIRED) location of the private key file to connect to hosts", required=True)
parser.add_argument('-u', '--user', dest='user', help="(REQUIRED) name of the user to SSH as", required=True)
parser.add_argument('-g', '--graphite-host', dest='graphite_host', help="(REQUIRED) hostname for your graphite instance", required=True)
parser.add_argument('-s', '--single-thread', action="store_true", dest='single_thread', help="(optional) go into single thread mode")

args = parser.parse_args()

# translate user input to python list
parsed_hostnames = [x for x in args.hostnames.split(',')]

if args.single_thread:
    get_procs_mem.MemCollector().get_mem_metrics_single(parsed_hostnames, args.p_key, args.user, args.graphite_host)
else:
    get_procs_mem.MemCollector().get_mem_metrics_multi(parsed_hostnames, args.p_key, args.user, args.graphite_host)
