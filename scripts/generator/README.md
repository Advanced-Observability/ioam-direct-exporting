# Scripts for the generator

The following scripts are used by the traffic generator to test the implementation of IOAM DEX:
- [`var_freq_dex.py`](./var_freq_dex.py) contains the packets that will be sent by TRex;
- [`test_profile_dex.py`](./test_profile_dex.py) is the script that will be executed by the scripts running on the DUT;

[`test_drop.py`](./test_drop.py) and [`drop_mtu.py`](./drop_mtu.py) are used for testing the forwarding capability of the Linux kernel.
