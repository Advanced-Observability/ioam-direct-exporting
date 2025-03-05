import os

# ---------------------------------------
#           COMMANDS
# ---------------------------------------

# IP IOAM commands
DEL_SCHEMA = "sudo ip ioam schema del 21"
DEL_NAMESPACE = "sudo ip ioam namespace del 123"
ADD_NAMESPACE = "sudo ip ioam namespace add 123 data 0x1234 wide 0x12345678"

# IP route commands
REMOVE_IP_ROUTE = "sudo /usr/bin/ip -6 r d cd00::/64"
VANILLA_IP_ROUTE = "sudo /usr/bin/ip -6 r a cd00::/64 via db02::1 dev ens6f1"
INLINE_IP_ROUTE = "sudo /usr/bin/ip -6 r a cd00::/64 encap ioam6 freq {}/{} mode inline dex ns 123 trace-type {} ext-flags {} via db02::1 dev ens6f1"
ENCAP_IP_ROUTE = "sudo /usr/bin/ip -6 r a cd00::/64 encap ioam6 freq {}/{} mode encap tundst db02::1 dex ns 123 trace-type {} ext-flags {} via db02::1 dev ens6f1"
ENCAP_TUNSRC_IP_ROUTE = "sudo /usr/bin/ip -6 r a cd00::/64 encap ioam6 freq {}/{} mode encap tunsrc db02::2 tundst db02::1 dex ns 123 trace-type {} ext-flags {} via db02::1 dev ens6f1"

# Path to python script to test profile file
RUN_PROFILE_FILE = "/opt/trex/v3.04/automation/trex_control_plane/interactive/trex/examples/stl/test_profile_dex.py"

# Exec formatted command on remote
EXEC_CMD_REMOTE = "ssh -i id_ed25519 -oStrictHostKeyChecking=no clt@merry.run.montefiore.uliege.be {}"

# ---------------------------------------
#           CODE
# ---------------------------------------

def check_root():
    return os.geteuid() == 0

def build_extra_data(ioamPacketName : str, nbMTU : int, nbIOAM : int, insertionDEX : bool, encapMode : bool):
    """Build parameters for `test_profile_dex.py`."""

    if ioamPacketName == "" and not insertionDEX:
        raise RuntimeError("ioam packet name cannot be empty")
    if nbMTU < 0 or nbIOAM < 0:
        raise RuntimeError("nbMTU and nbIOAM cannot be < 0")
    if nbMTU == 0 and nbIOAM == 0:
        raise RuntimeError("Cannot have both nbMTU and nbIOAM set to 0")

    extra = ""
    extra+=f"ioamPacketName={ioamPacketName},"
    extra+=f"nbMTU={nbMTU},"
    extra+=f"nbIOAM={nbIOAM},"
    extra+=f"insertionDEX={insertionDEX},"
    extra+=f"encapMode={encapMode}"

    return extra

def print_error(text: str):
    print(f"\033[91m[ERROR] {text}\033[0m")
