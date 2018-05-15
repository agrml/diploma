#! /usr/bin/python3

import os
import random
import sys
import signal

end = False

def sigint_handler(signal, frame):
    global end
    end = True
    print(end)

signal.signal(signal.SIGINT, sigint_handler)

path = '{}/fifo'.format(os.getcwd())
if not os.path.exists(path):
    os.mkfifo(path)
else:
    print('Writing to existing fifo...')
input('Open fifo for reading and press [Enter]:')
fifo = open(path, 'w')

while not end:
    x = 0.98
    fifo.write('{}\n'.format(x))
print('Closing fifo and ending...')
fifo.close()