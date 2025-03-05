"""
Usage: python3 test_profile_dex.py -n <nb_run> -e <extraData>.

Run tests <nb_run> times.

<extraData> will contain the following:
- ioamPacketName=<packetName>: name of the IOAM packet to insert in generated traffic. Look in `var_freq.py` for example;
- nbMTU=<nbMTU>: Number of MTU size packets (without IOAM) to send before sending IOAM packets;
- nbIOAM=<nbIOAM>: Number of <packetName> to send after sending the MTU packets without IOAM;
- insertionDEX=True|False: If True, will send packets smaller than MTU because DUT will add DEX;
- encapMode=True|False: If True, DUT will insert DEX in encap mode. If False, DUT will insert DEX in inline mode.

Example of usage:
python3 test_profile_dex.py -n 30 -e ioamPacketName=INLINE_PKT_OPTION0,nbMTU=10,nbIOAM=1,insertionDEX=False,encapMode=False

The file `var_freq_dex.py` must be in `/opt/trex/v3.04/stl`.

To put into /opt/trex/v3.04/automation/trex_control_plane/interactive/trex/examples/stl
on machine running TRex.
"""

import stl_path
from trex.stl.api import *
import sys
import pprint
import os
import argparse

# duration in seconds of each test
DURATION = 30

# default number of runs
NB_RUNS_DEFAULT = 30

# trex multiplicator - set to limit before dropping packets when Linux forwarding packets
MULT = "1150000pps"

# profile to use to generate traffic
PROFILE = "var_freq_dex.py"

# file in which to write the stats
OUTPUT_FILE = "/home/clt/stats.txt"

class TrexTestIOAM:
    """Represent TRex client. Wrapper on TRex client API."""

    def __init__(self, fileStats : str) -> None:
        """Save statistics inside `fileStats`."""

        self.file = open(fileStats, "a")
        self.client = STLClient(verbose_level = 'info')
        self.client.connect()
        self.client.reset()
        self.client.set_service_mode()

        print(f"Is connected? {self.client.is_connected()}")
        print(f"Nb ports: {self.client.get_port_count()}")

        self.acquiredPorts = self.client.get_acquired_ports()
        print(f"Acquired ports: {self.acquiredPorts}")

    def get_stats(self, port, print : bool):
        stats = self.client.get_stats([port])

        if print:
            pp = pprint.PrettyPrinter(depth=4)
            pp.pprint(stats)

        return stats

    def extract_stats(self):
        stats = self.get_stats(0, False)
        pps = stats[1]['rx_pps']
        bps = stats[1]['rx_bps']
        ipackets = stats['total']['ipackets']
        opackets = stats['total']['opackets']
        return pps, bps, ipackets, opackets

    def test_profile(self, extra : str):
        """Launch test using optional `extra` data."""

        # clean before running test
        self.clear_stats()
        self.client.reset(ports=self.acquiredPorts)

        # load var_freq.py profile file
        profile_file = os.path.join(stl_path.STL_PROFILES_PATH, PROFILE)
        profile=None
        try:
            profile = STLProfile.load_py(profile_file, **{"extra": extra})
        except STLError as e:
            print("\nError while loading profile'{0}'\n".format(profile_file))
            print(e.brief() + "\n")
            sys.exit(-1)

        # launch test for 30s
        self.client.remove_all_streams(self.acquiredPorts)
        self.client.add_streams(profile.get_streams(), ports=[0])
        self.client.start(ports=[0], mult=MULT, duration=DURATION)

        # wait for end
        try:
            self.client.wait_on_traffic(ports=self.acquiredPorts, timeout=DURATION)
        except:
            pass

        # get stats and write to file
        pps, bps, ipackets, opackets = self.extract_stats()
        self.file.write(f"{extra};{pps};{bps};{ipackets};{opackets}\n")

    def clear_stats(self):
        self.client.clear_stats(self.acquiredPorts)

    def disconnect(self):
        self.file.close()
        self.client.disconnect()

def check_arguments():
    """Check and parse arguments."""

    parser = argparse.ArgumentParser(
        prog="Tests",
        description="Run tests using the given extra data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-n", type=int, required=False, default=NB_RUNS_DEFAULT, help="Number of runs")
    parser.add_argument("-e", type=str, required=False, default="", help="Extra values")
    args = parser.parse_args()

    nbRun = int(args.n)
    extra = args.e

    if nbRun <= 0:
        print("<nb_run> cannot be <= 0")
        sys.exit(-1)

    return nbRun, extra

if __name__ == "__main__":
    nbRun, extra = check_arguments()

    t = TrexTestIOAM(OUTPUT_FILE)

    print(f"\n\nStarting {nbRun} runs of {DURATION}s each...")
    for i in range(nbRun):
        print(f"Run {i+1}/{nbRun}...")
        t.test_profile(extra)

    t.disconnect()
