"""
TRex profile for a packet of 1500 bytes (default Ethernet MTU in Linux).
"""

from trex_stl_lib.api import *
import argparse

class STLS1(object):

    def create_stream (self):
        return STLStream( 
            packet = STLPktBuilder(
                pkt = Ether()/IPv6(src="ab00::1",dst="cd00::1")/Raw((1514-54)*'x')
            ),
            mode = STLTXCont()
        )

    def get_streams (self, tunables, **kwargs):
        parser = argparse.ArgumentParser(description='Argparser for {}'.format(os.path.basename(__file__)), 
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        args = parser.parse_args(tunables)
        # create 1 stream 
        return [ self.create_stream() ]


# dynamic load - used for trex console or simulator
def register():
    return STLS1()
