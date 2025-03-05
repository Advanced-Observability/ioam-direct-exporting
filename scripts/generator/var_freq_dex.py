"""
Profile file that can insert the specified amount of IOAM data
after sending the given amount of MTU packets without IOAM.

Intended to be used with `test_profile_dex.py`.

To put into `/opt/trex/v3.04/stl` on machine running TRex.
"""

from trex_stl_lib.api import *
import argparse

class STLS1(object):

    def create_stream (self, ioamPacketName : str, nbMTU = 100, nbIOAM = 1, insertionDEX = False, encapMode = True):
        """
        Create stream which generates `nbMTU` MTU packets without IOAM followed by `nbIOAM` IOAM packets.

        Parameters:
        - `ioamPacketName` : which IOAM packet to generate. Must match one of the constants below.
        - `nbMTU`: number of MTU packets to generate.
        - `nbIOAM`: number of IOAM packets to generate.
        - `insertionDEX`: DEX will be inserted by DUT.
        - `encapMode`: DUT will insert PTO in encap mode instead of inline mode.
        """

        if nbMTU == 0 and nbIOAM == 0:
            raise RuntimeError("Cannot have both nbIOAM and nbMTU equal to 0")

        base_pkt = STLS1.PKT_MTU

        if insertionDEX:
            ioam_pkt = STLS1.DEX_ENCAP if encapMode else STLS1.DEX_INLINE
        else:
            ioam_pkt = STLS1.get_ioam_packet(ioamPacketName)

        if nbMTU == 0 or insertionDEX: # only IOAM packets
            return STLProfile(
                [
                    STLStream(
                        name       = 'ioam',
                        packet     = STLPktBuilder(pkt = ioam_pkt),
                        mode       = STLTXCont(percentage = 100),
                    ),
                ]
            ).get_streams()
        elif nbIOAM == 0: # only mtu packets
            return STLProfile(
                [
                    STLStream(
                        name       = 'mtu',
                        packet     = STLPktBuilder(pkt = base_pkt),
                        mode       = STLTXCont(percentage = 100),
                    ),
                ]
            ).get_streams()
        else: # mix of ioam and mtu packets
            total = nbMTU + nbIOAM
            ioamPercent = (nbIOAM/total)*100
            mtuPercent = (nbMTU/total)*100

            return STLProfile(
                [
                    STLStream(
                        name   = 'mtu',
                        packet = STLPktBuilder(pkt = base_pkt),
                        mode   = STLTXCont(percentage = mtuPercent),
                    ),
                    STLStream(
                        name       = 'ioam',
                        packet     = STLPktBuilder(pkt = ioam_pkt),
                        mode       = STLTXCont(percentage = ioamPercent),
                    ),
                ]
            ).get_streams()

    def get_streams(self, **kwargs):
        "Called from test_profile_dex.py to get the structure of the packets to generate."

        tunables = kwargs['extra']
        parser = argparse.ArgumentParser(
            description='Argparser for {}'.format(os.path.basename(__file__)),
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument("--ioamPacketName", type=str, required=True, help="Name of IOAM packet")
        parser.add_argument("--nbMTU", type=int, required=True, help="Number of MTU packets without IOAM")
        parser.add_argument("--nbIOAM", type=int, required=True, help="Number of IOAM packets")
        parser.add_argument('--insertionDEX', default=False, type=lambda x: (str(x).lower() == 'true'), help="Packet with size for insertion of DEX")
        parser.add_argument('--encapMode', default=False, type=lambda x: (str(x).lower() == 'true'), help="Packet with size for insertion of DEX in encap mode")

        values = []
        for pair in tunables.split(","):
            key, value = pair.split("=")
            values.append(f"--{key}={value}")
        args = parser.parse_args(values)

        # create one or more streams depending on the options.
        return self.create_stream(args.ioamPacketName, args.nbMTU, args.nbIOAM, args.insertionDEX, args.encapMode)

    # ~ Simple packets ~
    PKT_MTU = Ether()/IPv6(src="ab00::1",dst="cd00::1")/ICMPv6EchoRequest(data='x'*1438)

    # Use the following packets for evaluating the IOAM encapsulating node
    # 2B (IPv6 EH header) + 2B (Padding) + 4B (IOAM header) + 8B (DEX header) = 16B
    DEX_INLINE = Ether()/IPv6(src="ab00::1",dst="cd00::1")/ICMPv6EchoRequest(data='x'*(1438-16))
    # Additional 40B due to the extra IPv6 header because encap mode
    DEX_ENCAP = Ether()/IPv6(src="ab00::1",dst="cd00::1")/ICMPv6EchoRequest(data='x'*(1438-16-40))

    INLINE_NO_EXT_800000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x80\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_400000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x40\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_200000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x20\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_100000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x10\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_40000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x04\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_20000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x02\x00\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_8000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x80\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_4000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x40\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)
    INLINE_NO_EXT_2000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x20\x00\x00')])/ICMPv6EchoRequest(data='x'*1422)

    INLINE_FLOW_800000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x12\x00\x04\x00\x7b\x00\x80\x80\x00\x00\x00\x0b\xdb\xe4\x0d\x01\x02\x00\x00')])/ICMPv6EchoRequest(data='x'*1414)
    INLINE_FLOW_SEQ_800000 = Ether()/IPv6(src="ab00::1",dst="cd00::1")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x12\x00\x04\x00\x7b\x00\xc0\x80\x00\x00\x00\x0b\xdb\xe4\x0d\x00\x00\x00\x01')])/ICMPv6EchoRequest(data='x'*1414)

    ENCAP_NO_EXT_800000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x80\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_400000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x40\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_200000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x20\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_100000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x10\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_40000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x04\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_20000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x02\x00\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_8000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x80\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_4000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x40\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_NO_EXT_2000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x0a\x00\x04\x00\x7b\x00\x00\x00\x20\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)

    ENCAP_FLOW_800000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x12\x00\x04\x00\x7b\x00\x80\x80\x00\x00\x00\x0b\xdb\xe4\x0d\x01\x02\x00\x00')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)
    ENCAP_FLOW_SEQ_800000 = Ether()/IPv6(src="ab00::1",dst="db01::2")/IPv6ExtHdrHopByHop(options=[HBHOptUnknown(b'\x01\x00\x31\x12\x00\x04\x00\x7b\x00\xc0\x80\x00\x00\x00\x0b\xdb\xe4\x0d\x00\x00\x00\x01')])/IPv6(src="ab00::1", dst="cd00::1")/ICMPv6EchoRequest(data='x'*1382)

    # map between packet name and object
    PACKETS_DICT = {
        "INLINE_NO_EXT_800000": INLINE_NO_EXT_800000,
        "INLINE_NO_EXT_400000": INLINE_NO_EXT_400000,
        "INLINE_NO_EXT_200000": INLINE_NO_EXT_200000,
        "INLINE_NO_EXT_100000": INLINE_NO_EXT_100000,
        "INLINE_NO_EXT_40000": INLINE_NO_EXT_40000,
        "INLINE_NO_EXT_20000": INLINE_NO_EXT_20000,
        "INLINE_NO_EXT_8000": INLINE_NO_EXT_8000,
        "INLINE_NO_EXT_4000": INLINE_NO_EXT_4000,
        "INLINE_NO_EXT_2000": INLINE_NO_EXT_2000,

        "INLINE_FLOW_800000": INLINE_FLOW_800000,
        "INLINE_FLOW_SEQ_800000": INLINE_FLOW_SEQ_800000,

        "ENCAP_NO_EXT_800000": ENCAP_NO_EXT_800000,
        "ENCAP_NO_EXT_400000": ENCAP_NO_EXT_400000,
        "ENCAP_NO_EXT_200000": ENCAP_NO_EXT_200000,
        "ENCAP_NO_EXT_100000": ENCAP_NO_EXT_100000,
        "ENCAP_NO_EXT_40000": ENCAP_NO_EXT_40000,
        "ENCAP_NO_EXT_20000": ENCAP_NO_EXT_20000,
        "ENCAP_NO_EXT_8000": ENCAP_NO_EXT_8000,
        "ENCAP_NO_EXT_4000": ENCAP_NO_EXT_4000,
        "ENCAP_NO_EXT_2000": ENCAP_NO_EXT_2000,

        "ENCAP_FLOW_800000": ENCAP_FLOW_800000,
        "ENCAP_FLOW_SEQ_800000": ENCAP_FLOW_SEQ_800000,
    }

    def get_ioam_packet(name : str):
        """Return IOAM packet with given `name`."""

        if name not in STLS1.PACKETS_DICT:
            raise RuntimeError(f"Invalid IOAM packet name {name}")

        return STLS1.PACKETS_DICT[name]

# dynamic load - used for trex console or simulator
def register():
    return STLS1()
