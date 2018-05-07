#! /usr/bin/python3

import os

class Base:
    def __init__(self):
        self.bootstrap_env()

    def bootstrap_env(self):
        pass



class Host(Base):
    """Note: you have to run traffic manually when all the system is set up"""

    def __init__(self):
        super().__init__()

    def bootstrap_env(self):
        cmds = ['ip link add IntSourceIn type dummy',
                'ip addr add 192.168.57.1/24 dev IntSourceIn',
                'ip link set IntSourceIn up',
                # route to Iperf server on IntSink
                'ip route add 11.11.10.0/24 dev IntSourceIn',

                'ip link add IntSourceOut type veth peer name IntSinkIn',
                'ip link set IntSourceOut up',
                'ip link set IntSinkIn up',
                
                # elmulate packet loss on connection. 2% random loss with 25% correlation
                'tc qdisc changedev IntSourceOut netem loss 2% 25%'
                ]
        for cmd in cmds:
            os.system(cmd)

    def run_traffic(self):
        os.system('iperf -c 11.11.10.1')


class IntNode(Base):
    def __init__(self):
        super().__init__()

    def run_dpdk_setup(self):
        os.system('../???/???')
        # ./setup.py
        # 17
        # 20 -> 64
        # 23 -> 0000:00:08.0
        # 23 -> 0000:00:09.0
        #
        # ./build/l2fwd -c 0x3 -n 4 -- -p 3

    def run_c(self):
        """Note: Don't forget to select mode in C code"""
        # TODO: make
        os.system('./build/l2fwd -c 0x3 -n 4 -- -p 3')


class IntSource(IntNode):
    def __init__(self):
        super().__init__()
        self.run_dpdk_setup()
        self.run_c()


class IntSink(IntNode):
    def __init__(self):
        super().__init__()
        self.start_iperf_server()
        self.run_dpdk_setup()
        self.run_analyzer()
        self.run_c()

    def bootstrap_env(self):
        cmds = ['ip link add DpdkOut type veth peer name LinuxIn',
                'ip addr add 11.11.10.1/24 dev LinuxIn',
                'ip link set LinuxIn up',
                # route to Iperf client on host
                'ip route add 192.168.57.0/24 dev LinuxIn'
               ]
        for cmd in cmds:
            os.system(cmd)

    def start_iperf_server(self):
        os.system('iperf -s')

    def run_analyzer(self):
