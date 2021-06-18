#!/usr/bin/env python2
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../utils/")
)

import p4runtime_lib.bmv2
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper


def get_packets_and_bytes(p4info_helper, sw, counter_name, index):
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            return counter.data.packet_count, counter.data.byte_count


def main(p4info_file_path, bmv2_file_path):
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name="s1",
            address="127.0.0.1:50051",
            device_id=0,
            proto_dump_file="logs/s1-p4runtime-counter.txt",
        )
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name="s2",
            address="127.0.0.1:50052",
            device_id=1,
            proto_dump_file="logs/s2-p4runtime-counter.txt",
        )
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name="s3",
            address="127.0.0.1:50053",
            device_id=2,
            proto_dump_file="logs/s3-p4runtime-counter.txt",
        )

        def packets_and_bytes(switch, port):
            return get_packets_and_bytes(
                p4info_helper, switch, "MyIngress.traffic_counter", port
            )

        switches = [s1, s2, s3]
        ports = [1, 2, 3]

        max_window = 3600

        data = {}
        for s in switches:
            for p in ports:
                data[s.name, p] = [(0, 0) for _ in range(max_window)]

        def summary(window):
            print "=== Last %s seconds summarry ===" % window
            for s in switches:
                for p in ports:
                    prev_packets, prev_bytes = data[s.name, p][-window]
                    curr_packets, curr_bytes = data[s.name, p][-1]
                    packets, bytes = (
                        curr_packets - prev_packets,
                        curr_bytes - prev_bytes,
                    )
                    print "%s %s: %s (%s bytes)" % (s.name, p, packets, bytes)
            print ""

        time = 1

        while True:
            for s in switches:
                for p in ports:
                    data[s.name, p].pop(0)
                    data[s.name, p].append(packets_and_bytes(s, p))

            if time % 60 == 0:
                summary(60)

            if time % 5 == 0:
                summary(5)

            time += 1
            sleep(1)

    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4Runtime Controller")
    parser.add_argument(
        "--p4info",
        help="p4info proto in text format from p4c",
        type=str,
        action="store",
        required=False,
        default="./build/traffic_monitoring.p4.p4info.txt",
    )
    parser.add_argument(
        "--bmv2-json",
        help="BMv2 JSON file from p4c",
        type=str,
        action="store",
        required=False,
        default="./build/traffic_monitoring.json",
    )
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
