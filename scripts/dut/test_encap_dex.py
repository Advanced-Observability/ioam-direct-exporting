"""
Usage: sudo python3 test_encap_dex.py

Test encap of IOAM DEX.
To run on DUT.

`var_freq_dex.py` must be in `/opt/trex/v3.04/stl` on the machine running TRex.
"""

from utilities import *
from enum import Enum
import os, sys

# ---------------------------------------
#           SETTINGS
# ---------------------------------------

# Frequencies of IOAM - 0.001%, 0.01%, 0.1%, 1%, 5%, 10%, 25%, 50%, 100%
NB_MTUS = [99999, 9999, 999, 99, 19, 9, 3, 1, 0]
NB_IOAMS = [1, 1, 1, 1, 1, 1, 1, 1, 1]

# Nb runs of each test
NB_ITERS = 10

# Enable dry run mode
DRY_RUN = True

# Enable/disable individual test
TEST_MODE = True
TEST_EXT_FLAG = True
TEST_DATA_FIELD = True

# ---------------------------------------
#           PARAMETERS
# ---------------------------------------

# IOAM DEX extension flags: flow id / flow id + seq num
EXT_FLAGS = ["0x00", "0x80", "0xC0"]

# IOAM data fields
DATA_FIELDS = ["0x800000", "0x400000", "0x200000", "0x100000", "0x40000", "0x20000", "0x8000", "0x4000", "0x2000"]

class Mode(Enum):
    INLINE = 1
    ENCAP = 2
    ENCAP_TUNSRC = 3

# ---------------------------------------
#           CODE
# ---------------------------------------

# --- TEST METHODS ---

def run_tests_mode(mode : Mode, nbMTU : int, nbIOAM : int):
    """
    Test in different modes with a single data field (bit 0) and no extension flags.
    """

    if mode == Mode.INLINE:
        print(f"Running test on mode inline with and frequencies {nbMTU}/{nbIOAM}...")
    elif mode == Mode.ENCAP:
        print(f"Running test on mode encap with and frequencies {nbMTU}/{nbIOAM}...")
    elif mode == Mode.ENCAP_TUNSRC:
        print(f"Running test on mode encap tunsrc with and frequencies {nbMTU}/{nbIOAM}...")
    else:
        print_error("Unexpected mode!")
        sys.exit(-1)

    if DRY_RUN:
        return

    os.system(REMOVE_IP_ROUTE)

    if mode == Mode.INLINE and os.system(INLINE_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, "0x800000", "0x00")):
        print_error(f"Could not add route with extflag 0x00 in {mode} mode")
        sys.exit(-1)
    elif mode == Mode.ENCAP and os.system(ENCAP_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, "0x800000", "0x00")):
        print_error(f"Could not add route with extflag 0x00 in {mode} mode")
        sys.exit(-1)
    elif mode == Mode.ENCAP_TUNSRC and os.system(ENCAP_TUNSRC_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, "0x800000", "0x00")):
        print_error(f"Could not add route with extflag 0x00 in {mode} mode")
        sys.exit(-1)

    # launch trex on remote machine
    # name of packet does not matter because it will be replaced by another one inside var_freq_dex.py
    encap = True if mode == Mode.ENCAP or mode == Mode.ENCAP_TUNSRC else False
    data = build_extra_data("", nbMTU, nbIOAM, True, encap)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print_error(f"Could not launch TRex with mode {mode} and extflag 0x00")
        sys.exit(-2)

    # save stats on remote machine
    destFilename = f"encap_mode_{mode}_{nbMTU}_{nbIOAM}_stats.txt"
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.txt {destFilename}")) != 0:
        print_error(f"Could not save the stats on the remote machine for {mode} with extflag 0x00")
        sys.exit(-3)

def run_tests_extflag(extflag : str, nbMTU : int, nbIOAM : int):
    """
    Test in inline mode with a single data field (bit 0) and different extension flags.
    """

    print(f"Running test on extflag {extflag} and frequencies {nbMTU}/{nbIOAM}...")

    if DRY_RUN:
        return

    os.system(REMOVE_IP_ROUTE)

    if os.system(INLINE_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, "0x800000", extflag)):
        print_error(f"Could not add route with extflag {extflag} in inline mode")
        sys.exit(-1)

    # launch trex on remote machine
    # name of packet does not matter because it will be replaced by another one inside var_freq_dex.py
    data = build_extra_data("", nbMTU, nbIOAM, True, False)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print_error(f"Could not launch TRex with mode inline and extflag {extflag}")
        sys.exit(-2)

    # save stats on remote machine
    destFilename = f"encap_extflag_{extflag}_{nbMTU}_{nbIOAM}_stats.txt"
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.txt {destFilename}")) != 0:
        print_error(f"Could not save the stats on the remote machine for mode inline with extflag {extflag}")
        sys.exit(-3)

def run_tests_trace_type(field : str, nbMTU : int, nbIOAM : int):
    """
    Test in inline mode with different data fields and no extension flag.
    """

    print(f"Running test on data field {field} and frequencies {nbMTU}/{nbIOAM}...")

    if DRY_RUN:
        return

    os.system(REMOVE_IP_ROUTE)

    if os.system(INLINE_IP_ROUTE.format(nbIOAM, nbIOAM+nbMTU, field, "0x00")):
        print_error(f"Could not add route with data field {field} in inline mode")
        sys.exit(-1)

    # launch trex on remote machine
    # name of packet does not matter because it will be replaced by another one inside var_freq_dex.py
    data = build_extra_data("", nbMTU, nbIOAM, True, False)
    if os.system(EXEC_CMD_REMOTE.format(f"python3 {RUN_PROFILE_FILE} -n {NB_ITERS} -e {data}")) != 0:
        print_error(f"Could not launch TRex with mode inline and data field {field}")
        sys.exit(-2)

    # save stats on remote machine
    destFilename = f"encap_data_{field}_{nbMTU}_{nbIOAM}_stats.txt"
    if os.system(EXEC_CMD_REMOTE.format(f"mv stats.txt {destFilename}")) != 0:
        print_error(f"Could not save the stats on the remote machine for mode inline with data field {field}")
        sys.exit(-3)

# --- MAIN ---

if __name__ == "__main__":
    if not check_root():
        print_error("Must be running as root")
        sys.exit(-1)

    if not len(NB_IOAMS) == len(NB_MTUS):
        raise RuntimeError("Cannot have NB_IOAMS and NB_MTUS with different length")

    # run test on mode
    if TEST_MODE:
        print("\n~ Test on mode... ~\n")
        for i in range(len(NB_MTUS)):
            run_tests_mode(Mode.INLINE, NB_MTUS[i], NB_IOAMS[i])
            run_tests_mode(Mode.ENCAP, NB_MTUS[i], NB_IOAMS[i])
            run_tests_mode(Mode.ENCAP_TUNSRC, NB_MTUS[i], NB_IOAMS[i])

    # run test on extflag
    if TEST_EXT_FLAG:
        print("\n~ Test on extension flags... ~\n")
        for i in range(len(NB_MTUS)):
            for extflag in EXT_FLAGS:
                run_tests_extflag(extflag, NB_MTUS[i], NB_IOAMS[i])

    # run test on data field
    if TEST_DATA_FIELD:
        print("\n~ Test on data fields... ~\n")
        for i in range(len(NB_MTUS)):
            for field in DATA_FIELDS:
                run_tests_trace_type(field, NB_MTUS[i], NB_IOAMS[i])

    sys.exit(0)
