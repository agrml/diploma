#! /usr/bin/python3

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
        print('''Host is ready. Your actions now:
0. Check IntSourceIn/Out inserted to VM-1 and IntSinkIn to VM-2.
1. Launch VMs.
2. Run that script at them:
VM-1: ssh kim@127.0.0.1 -p 8025
VM-2: ssh kim@127.0.0.1 -p 8026
3. Run self.run_traffic() at Host.''')

    def bootstrap_env(self):
        cmds = ['ip link add IntSourceIn type dummy',
                'ip addr add 192.168.57.1/24 dev IntSourceIn',
                'ip link set IntSourceIn up',
                # route to iperf server
                'ip route add 11.11.10.0/24 dev IntSourceIn',

                'ip link add IntSourceOut type veth peer name IntSinkIn',
                'ip link set IntSourceOut up',
                'ip link set IntSinkIn up'
                
                # iperf server
                'ip netns add iperf',
                'ip netns exec iperf ip link add IntSinkOut type dummy',
                'ip netns exec iperf ip addr add 11.11.10.1/24 dev IntSinkOut',
                'ip netns exec iperf ip ip link set IntSinkOut up',
                # route to iperf client
                'ip netns exec iperf ip route add 192.168.57.0/24 dev IntSinkOut'


                # elmulate packet loss on connection. 2% random loss with 25% correlation
                'tc qdisc add dev IntSourceOut root netem loss 0.02 0.25'
                ]
        for cmd in cmds:
            os.system(cmd)

    def run_traffic(self):
        os.system('iperf -s')
        os.system('iperf -c 11.11.10.1')


class IntNode(Base):
    """Interface"""

    def __init__(self):
        super().__init__()

    def run_dpdk_setup(self):
        print('''Entering DPDK\' setup.sh...
Select the following:
17
20 -> 64
23 -> 0000:00:08.0
23 -> 0000:00:09.0
''')
        os.system('../../tools/setup.sh')

    def run_c(self):
        print('Assing correct value to the global variable in C code')
        input('Continue? [Enter]: ')
        os.system('export RTE_SDK=/home/kim/dpdk && export RTE_TARGET=build && ./build/l2fwd -c 0x3 -n 4 -- -p 3')

class IntSource(IntNode):
    def __init__(self):
        super().__init__()
        self.run_dpdk_setup()
        self.run_c()


class IntSink(IntNode):
    def __init__(self):
        super().__init__()
        self.run_dpdk_setup()
        self.run_analyzer()
        self.run_c()

    def run_analyzer(self):
        os.system('./analyzer.py')
        # TODO: path in argv

