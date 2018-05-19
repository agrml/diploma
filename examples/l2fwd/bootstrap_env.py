#! /usr/bin/python3

import argparse
import os

class Base:
    """Interface"""

    def __init__(self):
        self.bootstrap_env()

    def bootstrap_env(self):
        pass



class Host(Base):
    def __init__(self):
        super().__init__()
        input('''Host is ready. Your actions now:
0. Check IntSourceIn/Out inserted to VM-1 and IntSinkIn to VM-2.
1. Launch VMs.
2. Run that script at them:
    VM-1: ssh kim@127.0.0.1 -p 8025
    VM-2: ssh kim@127.0.0.1 -p 8026
3. Run server when ready [Enter]: ''')
        print('For running traffic exec manually `iperf -c 11.11.10.1`')
        self.run_server()

    def bootstrap_env(self):
        cmds = ['ip link add IntSourceIn type dummy',
                'ip addr add 192.168.57.1/24 dev IntSourceIn',
                'ip link set IntSourceIn up',
                # route to iperf server
                'ip route add 11.11.10.0/24 dev IntSourceIn',

                # ns-2 for iperf server
                'ip netns add ns-2',

                # connect two ns
                'ip link add IntSourceOut type veth peer name IntSinkIn netns ns-2',
                'ip link set IntSourceOut up',

                # ns-2 IntSinkIn
                'ip netns exec ns-2 ip link set IntSinkIn up',
                # ns-2 IntSinkOut
                'ip netns exec ns-2 ip link add IntSinkOut type dummy',
                'ip netns exec ns-2 ip addr add 11.11.10.1/24 dev IntSinkOut',
                'ip netns exec ns-2 ip link set IntSinkOut up',
                # route to iperf client
                'ip netns exec ns-2 ip route add 192.168.57.0/24 dev IntSinkOut',


                # elmulate packet loss on connection. 2% random loss with 25% correlation
                'tc qdisc add dev IntSourceOut root netem loss 0.02 0.25'
                ]
        for cmd in cmds:
            os.system(cmd)

    def run_server(self):
        os.system('ip netns exec ns-2 iperf -s')


class IntNode(Base):
    """Interface"""

    def __init__(self):
        super().__init__()

    def run_dpdk_setup(self):
        print('''Entering DPDK\'s setup.sh...
Select the following:
17
20 -> 64
23 -> 0000:00:08.0
23 -> 0000:00:09.0
''')
        os.system('../../tools/setup.sh')


class IntSource(IntNode):
    def __init__(self):
        super().__init__()
        self.run_dpdk_setup()
        self.run_c()

    def run_c(self):
        os.system('export RTE_SDK=/home/kim/dpdk && export RTE_TARGET=build && ./build/l2fwd -c 0x3 -n 4 -- -p 3 -m 1')

class IntSink(IntNode):
    def __init__(self):
        super().__init__()
        self.run_dpdk_setup()
        self.run_analyzer()
        self.run_c()

    def run_analyzer(self):
        os.system('./analyzer.py fifo')

    def run_c(self):
        os.system('export RTE_SDK=/home/kim/dpdk && export RTE_TARGET=build && ./build/l2fwd -c 0x3 -n 4 -- -p 3 -m 2')

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('role', help='Role: Host/IntSource/IntSink')
args = parser.parse_args()
if args.role == 'Host':
    me = Host()
elif args.role == 'IntSource':
    me = IntSource()
elif args.role == 'IntSink':
    me = IntSink()
else:
    print('Incorrect mode. Exiting...')


