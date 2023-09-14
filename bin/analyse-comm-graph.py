#!/usr/bin/env python3
# coding: utf-8
#
"""Analyse the binary communication graph dumpped by mpiP."""

import struct
import argparse
import json
import os
import functools


def parse_graph(fn):
    s1 = "ii"  # proc messages header
    s2 = "di"  # message descriptor
    s1s = struct.calcsize(s1)
    s2s = struct.calcsize(s2)
    with open(fn, "rb") as f:
        buf = f.read()
    result = {}
    offset = 0
    while True:
        pid, msg_count = struct.unpack_from(s1, buf, offset)
        offset += s1s
        result[pid] = []
        for _ in range(msg_count):
            dest, size = struct.unpack_from(s2, buf, offset)
            offset += s2s
            result[pid].append([dest, int(size)])
        if offset >= len(buf):
            break
    return result


def dump_graph(graph, fn):
    with open(fn, "w", encoding="utf8", newline="\n") as f:
        json.dump(graph, f)


def analyse_graph(graph):
    nprocs = len(graph)
    nmsgs = functools.reduce(lambda x, y: x + y,
                             (len(x) for x in graph.values()), 0)
    print("Communication graph summary:")
    print(f"  {nprocs} processes")
    print(f"  {nmsgs} messages")


def main():
    parser = argparse.ArgumentParser(prog=os.path.basename(__file__),
                                     description=__doc__)
    parser.add_argument("GRAPH_FILE",
                        help="Communication graph dumpped by mpiP")
    parser.add_argument("-d",
                        "--dump-to",
                        default=None,
                        help="Dump the graph to json format")
    args = parser.parse_args()

    graph = parse_graph(args.GRAPH_FILE)
    analyse_graph(graph)
    if args.dump_to is not None:
        dump_graph(graph, args.dump_to)


if __name__ == "__main__":
    main()
