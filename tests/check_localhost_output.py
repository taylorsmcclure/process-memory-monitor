#!/usr/bin/env python
import re

with open('metrics.log', 'r') as f:
    results = f.read()

results = re.sub('\[|\]|\'', '', results)

for i in results.split(','):
    split_list = list(filter(None, i.split(' ')))
    print('INFO: Testing memory metrics:\n{}'.format(split_list))
    for n in split_list[-3:]:
        try:
            split_list[split_list.index(n)] = int(n)
        except ValueError as e:
            print(e)
            print('TEST FAIL: {} is not a memory value, this must be an integer'.format(n))
            exit(1)

    if isinstance(split_list[0], str):
        pass
    else:
        print(split_list[0])
        print('TEST FAIL: {} is not a command'.format(split_list[0]))
        exit(1)

    print('INFO: Tests passed!')
    