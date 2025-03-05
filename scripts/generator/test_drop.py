"""
Usage: python3 test_drop.py

Tests for the max forwaded pps before drop.

Profile files must be in `/opt/trex/v3.04/stl` on the machine running TRex.

To put into /opt/trex/v3.04/automation/trex_control_plane/interactive/trex/examples/stl
on the machine running TRex.
"""

import stl_path
from trex.stl.api import *
import sys
import pprint
import os

MIN_PPS = 100000
MAX_PPS = 1500000+1
STEP = 100000

# duration in seconds
DURATION = 30

# number of iterations
NB_ITERS = 10

# files containing the structure of the packets
PROFILES = ["drop_mtu.py"]

class TrexTestIOAM:
    def __init__(self, fileStats : str) -> None:
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
        rxPps = stats['total']['rx_pps']
        txPps = stats['total']['tx_pps']
        ipackets = stats['total']['ipackets']
        opackets = stats['total']['opackets']
        dropRate = 1.0 - (stats['total']['ipackets']/stats['total']['opackets'])
        return rxPps, txPps, ipackets, opackets, dropRate

    def test_profile(self, filename : str, ppsLimit : int):
        """
        Launch test using given profile file.
        """
        # clean before running test
        self.clear_stats()
        self.client.reset(ports=self.acquiredPorts)

        # load profile file
        profile_file = os.path.join(stl_path.STL_PROFILES_PATH, filename)
        try:
            profile = STLProfile.load(profile_file)
        except STLError as e:
            print("\nError while loading profile'{0}'\n".format(profile_file))
            print(e.brief() + "\n")
            sys.exit(-1)

        # launch test for 30s
        self.client.remove_all_streams(self.acquiredPorts)
        self.client.add_streams(profile.get_streams(), ports=[0])
        self.client.start(ports=[0], mult=f"{ppsLimit}pps", duration=DURATION)

        # wait for end
        self.client.wait_on_traffic(ports=self.acquiredPorts)

        # get drop rate and write to file
        rx, tx, ipkts, opkts, dropRate  = self.extract_stats()
        print(f"pps = {ppsLimit} | rx = {rx} | tx = {tx} | ipkts = {ipkts} | opkts = {opkts} | drop = {dropRate}")
        self.file.write(f"{ppsLimit};{rx};{tx};{ipkts};{opkts};{dropRate}\n")

    def clear_stats(self):
        self.client.clear_stats(self.acquiredPorts)

    def disconnect(self):
        self.file.close()
        self.client.disconnect()

def test_profile(filename : str):
    """Test `filename` profile."""

    t = TrexTestIOAM(f"/home/clt/stats_{filename}.txt")

    for i in range(MIN_PPS, MAX_PPS, STEP):
        print(f"\nTesting with PPS = {i}\n")
        for j in range(NB_ITERS):
            print(f"Run {j}/{NB_ITERS}")
            t.test_profile(filename, i)

    t.disconnect()

if __name__ == "__main__":

    for profile in PROFILES:
        print(f"\n\n~~ Testing profile {profile} ~~\n")
        test_profile(profile)

    sys.exit(0)
