#!/usr/bin/env python3
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper

def writeIPV4LpmDefault(p4info_helper, ingress_sw, dst_ip, dst_mac, egress_port):

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm1",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip, 32),
            "hdr.ipv4.diffserv": 0
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_mac,
            "port": egress_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ipv4_lpm1 (default) rule on %s" % ingress_sw.name)

def writeBackup_1(p4info_helper, ingress_sw, dst_ip, dst_mac, egress_port):

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm2",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip, 32),
            "hdr.ipv4.diffserv": 4
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_mac,
            "port": egress_port,
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ipv4_lpm2 (backup_1) rule on %s" % ingress_sw.name)

def writeBackup_2(p4info_helper, ingress_sw, dst_ip, dst_mac, egress_port):

    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm3",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip, 32),
            "hdr.ipv4.diffserv": 8
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dst_mac,
            "port": egress_port
        })
    ingress_sw.WriteTableEntry(table_entry)
    print("Installed ipv4_lpm3 (backup_2) rule on %s" % ingress_sw.name)


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            print(entry)
            print('-----')


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')

        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')

        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()


        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s3")
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s4")
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s5")

        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s6")

        # ====================================================================== default (ipv4_lpm1) ============================================
        #write S1 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:11", egress_port=1)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=3) #from s3 -> s6 -> s4
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S2 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:22", egress_port=1)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=4)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S3 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:33", egress_port=1)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=4)

        #write S4 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:44", egress_port=1)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S5 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:55", egress_port=1)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S6 rules
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=2)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeIPV4LpmDefault(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:66", egress_port=1)

        # ============================================================backup1 (ipv4_lpm2)=========================================================
        #write S1 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:11", egress_port=1)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=3) 
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S2 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:22", egress_port=1)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S3 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:33", egress_port=1)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=4)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=4)

        #write S4 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:44", egress_port=1)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S5 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:55", egress_port=1)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S6 rules
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=2)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeBackup_1(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:66", egress_port=1)


        #================================================================== backup2 (ipv4_lpm3) =============================================
        #write S1 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:11", egress_port=1)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=2) 
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s1, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=2)

        #write S2 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:22", egress_port=1)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s2, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=4)

        #write S3 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:33", egress_port=1)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s3, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=4)

        #write S4 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:44", egress_port=1)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s4, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S5 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=2)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:55", egress_port=1)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s5, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:00", egress_port=3)

        #write S6 rules
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.1.1", dst_mac="08:00:00:00:01:00", egress_port=3)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.2.2", dst_mac="08:00:00:00:02:00", egress_port=3)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.3.3", dst_mac="08:00:00:00:03:00", egress_port=3)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.4.4", dst_mac="08:00:00:00:04:00", egress_port=4)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.5.5", dst_mac="08:00:00:00:05:00", egress_port=3)
        writeBackup_2(p4info_helper=p4info_helper, ingress_sw=s6, dst_ip="10.0.6.6", dst_mac="08:00:00:00:06:66", egress_port=1)



        # TODO Uncomment the following two lines to read table entries from s1 and s2
        # readTableRules(p4info_helper, s1)
        # readTableRules(p4info_helper, s2)
        # readTableRules(p4info_helper, s3)
        # readTableRules(p4info_helper, s4)
        # readTableRules(p4info_helper, s5)
        # readTableRules(p4info_helper, s6)


    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/mrc.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/mrc.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
