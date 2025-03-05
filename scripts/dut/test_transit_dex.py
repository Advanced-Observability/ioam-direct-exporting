"""
Usage: sudo python3 test_transit_dex.py

Test transit with different IOAM options and different frequencies of IOAM packets.

To run on DUT.

`var_freq.py` must be in `/opt/trex/v3.04/stl` on the machine running TRex.
"""

from utilities import *
import os, sys

# ---------------------------------------
#           SETTINGS
# ---------------------------------------

# frequencies of IOAM - 0.001%, 0.01%, 0.1%, 1%, 5%, 10%, 25%, 50%, 100%
NB_MTUS = [99999, 9999, 999, 99, 19, 9, 3, 1, 0]
NB_IOAMS = [1, 1, 1, 1, 1, 1, 1, 1, 1]

# Number of runs of test
NB_ITERS = 10

# Enable dry run mode
DRY_RUN = True

# ---------------------------------------
#           PARAMETERS
# ---------------------------------------

# packet names
PACKET_NAMES = [
    "INLINE_NO_EXT_800000", "INLINE_NO_EXT_400000", "INLINE_NO_EXT_200000", "INLINE_NO_EXT_100000",
    "INLINE_NO_EXT_40000", "INLINE_NO_EXT_20000",
    "INLINE_NO_EXT_8000", "INLINE_NO_EXT_4000", "INLINE_NO_EXT_2000",
    "INLINE_FLOW_800000", "INLINE_FLOW_SEQ_800000"
]

# ---------------------------------------
#           CODE
# ---------------------------------------

def test(name: str, nbMTU: int, nbIOAM: int):
    """Test with given packet `name`."""

    print(f"\n\n~ Test transit with pkt {name} and frequencies {nbMTU}/{nbIOAM} ~\n")

    if DRY_RUN:
        return

    # launch trex on remote machine
    data = build_extra_data(name, nbMTU, nbIOAM, False, False)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print_error(f"Error while launching TRex with packet {name} with nbMTU = {nbMTU} and nbIOAM = {nbIOAM}")
        sys.exit(-2)

    # save stats on remote machine
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.txt transit_{name}_{nbMTU}_{nbIOAM}_stats.txt")) != 0:
        print_error(f"Error while saving the stats on the remote machine for packet {name} with nbMTU = {nbMTU} and nbIOAM = {nbIOAM}")
        sys.exit(-3)

if __name__ == "__main__":
    if not check_root():
        print("Must be running as root")
        sys.exit(-1)

    if not len(NB_IOAMS) == len(NB_MTUS):
        raise RuntimeError("Cannot have NB_IOAMS and NB_MTUS with different length")

    # config DUT
    os.system(DEL_SCHEMA)
    os.system(ADD_NAMESPACE)
    os.system(REMOVE_IP_ROUTE)
    os.system(VANILLA_IP_ROUTE)

    # test different options
    for name in PACKET_NAMES:
        for i in range(len(NB_MTUS)):
            test(name, NB_MTUS[i], NB_IOAMS[i])

    sys.exit(0)
