# IOAM Direct Exporting (DEX)

Implementation of IOAM Direct Exporting ([RFC 9326](https://datatracker.ietf.org/doc/rfc9326/)) in kernel and user spaces.

[Paper](https://orbi.uliege.be/handle/2268/328634): accepted at [NetDev 0x19](https://netdevconf.info/0x19/) conference.

![DEX](./architecture/dex.png)

## Linux Kernel

Implemention of DEX in Linux kernel reyling on lightweight tunnels.

Based on the [implementation](https://github.com/Advanced-Observability/ioam-linux-kernel) for IOAM Pre-allocated Trace Option-type (PTO) whil ensuring backward compatibility.

See [patch](./patches/linux.patch).

## iproute2

Add support to [iproute2](https://git.kernel.org/pub/scm/network/iproute2/iproute2.git) for configuring from user space lightweight tunnels to use IOAM DEX.

See [patch](./patches/iproute.patch).

## Wireshark

Our [patch](./patches/wireshark.patch) has been **merged** ([part 1](https://gitlab.com/wireshark/wireshark/-/merge_requests/16848) and [part 2](https://gitlab.com/wireshark/wireshark/-/merge_requests/18740)) in the [mainline repository](https://gitlab.com/wireshark/wireshark).

However, a new version has **not** been released since then.
Thus, you need to compile from the sources to benefit from our patch.
Please refer to Wireshark's [developer guide](https://www.wireshark.org/docs/wsdg_html_chunked/) for instructions on how to compile depending on your OS.

## IPFIX Exporter

It is a Go-based implementation for encoding and exporting IP Flow Information Export (IPFIX) messages of In Situ Operations, Administration, and Maintenance (IOAM) data.

See repository [ioam-exporter](https://github.com/Advanced-Observability/ioam-exporter).

## IPFIX Collector

For collecting IPFIX data, we rely on CESNET's [ipfixcol2](https://github.com/CESNET/ipfixcol2).

It can support IOAM DEX by using the custom [ioam_dex.xml](./ioam_dex.xml) file containing definition of IPFIX information elements.
