'''
Ethernet learning switch with a simple spanning tree protocal in Python.

'''
from switchyard.lib.userlib import *
from spanningtreemessage import SpanningTreeMessage
import collections
import time

# The implementation of the data structrue below is adapted from leetcode.
# https://leetcode.com/problems/lru-cache/discuss/45952/Python-concise-solution-with-comments-(Using-OrderedDict).
class FwdTable:
    def __init__(self, capacity):
        self.dic = collections.OrderedDict()
        self.remain = capacity

    # This function gets an entry in the table and modify the LRU order
    def getNmod(self, key):
        if key is None:
            print("Key is None!")
            return None
        if key not in self.dic:
            return None
        v = self.dic.pop(key)
        self.dic[key] = v # set key as the newest one
        return v

    # This function gets an entry in the table without modifying the LRU order
    def get(self, key):
        if key is None:
            print("Key is None!")
            return None
        if key not in self.dic:
            return None
        v = self.dic.get(key)
        return v


    def set(self, key, value):
        if key is None:
            print("Key is None!")
            return
        if value is None:
            print("Value is None!")
            return
        if key in self.dic:
            # update port info without modifying LRU order
            self.dic[key] = value
        else:
            if self.remain > 0:
                self.remain -= 1
            else:
                self.dic.popitem(last = False)
            # Not sure what could happen when key or value is None. Might cause problem.
            self.dic[key] = value

    def contain(self, key):
        if key is None:
            print("Key is None!")
            return False
        if key in self.dic:
            return True
        return False


def mk_stp_pkt(root_id, hops, hwsrc="20:00:00:00:00:01", hwdst="ff:ff:ff:ff:ff:ff"):
    spm = SpanningTreeMessage(root=root_id, hops_to_root=hops)
    Ethernet.add_next_header_class(EtherType.SLOW, SpanningTreeMessage)
    pkt = Ethernet(src=hwsrc,
                   dst=hwdst,
                   ethertype=EtherType.SLOW) + spm
    xbytes = pkt.to_bytes()
    p = Packet(raw=xbytes)
    return p


def main(net):
    my_interfaces = net.interfaces() 
    mymacs = [intf.ethaddr for intf in my_interfaces]
    # Set up the forwarding table
    TABLE_CAPACITY = 5
    fwdTable = FwdTable(TABLE_CAPACITY)

    # 1. Add id to the switch, in this case the smallest MAC address among all addresses.

    min_mac = mymacs[0]
    for mac in mymacs:
        # log_debug(mac)
        if mac < min_mac:
            min_mac = mac
    # log_debug(min_mac)
    switch_id = min_mac

    # 2. Import the packet header type in spanningtreemessage.py

    # 3. When the switch starts up, it floods out stp packets(to determine the root).

    #    Need to store a few things: 

    #    id of the current root(initialized to the switch's own id)
    #    the number of hops to the root (initialized to 0)
    #    the time at which the last spanning tree message was received
    
    #    Each non-root node also needs to remember which interface on which spanning tree message from the perceived root arrives.

    root_id = switch_id
    root_hop_num = 0
    # Initialize time to be 0. Not sure if this will cause problem.
    time_last_stpmsg = 0
    port_root_stpmsg = None

    # Set up fwding mode dictionary

    fwdModeDict = {}

    # 4. Only root node generate STP packets periodically. Initially, a node assumes that it is the root.

    #    These packets are initialized with the switch's own id and 0 as the number of hops to the root.
    #    The root node should emit new stp packets every 2 seconds.
    #    All the ports of the router will be in forwarding mode.
    time_last_fwding = time.time()
    # Forward packets on all ports
    for intf in my_interfaces:
        # Set this interface to forwarding mode
        fwdModeDict[intf] = True
        log_debug(fwdModeDict[intf])
        # Create a stp packet
        stpPkt = mk_stp_pkt(root_id, root_hop_num)
        log_debug ("Flooding packet {} to {}".format(stpPkt, intf.name))
        net.send_packet(intf.name, stpPkt)



    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            curr_time = time.time()
            # Send packets every 2 seconds
            if root_id == switch_id and curr_time - time_last_fwding >= 2:
                time_last_fwding = curr_time
                # Forward packets on all ports
                for intf in my_interfaces:
                    # Create a stp packet
                    stpPkt = mk_stp_pkt(root_id, root_hop_num)
                    log_debug ("Flooding packet {} to {}".format(stpPkt, intf.name))
                    net.send_packet(intf.name, stpPkt)
            continue
        except Shutdown:
            return

        # Apparently the LRU Cache data structure is needed.
        # Each entry in the table is in the form of (src, port)
        # src, in this case, is packet[0].src
        # port, in this case, is input_port

        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))

        # Determine if the packet is a spanning tree packet

        if packet[0].ethertype == EtherType.SLOW:

            # Record the time of last spanning tree msg
            time_last_stpmsg = time.time()
            log_debug("This is a spanning tree packet!")

            # 5. When a node receives a spanning tree packet it examines the root attribute:

            # a. If the id in the received packet is smaller than the id that the node currently thinks is the root, 
            #    the id in the received packet becomes the new root.
            #    The node should then forward the packet out all interfaces except for the one on which the packet was received.
            #    Prior to forwarding, the number of hops to the root should be incremented by 1.
            #    The interface on which the spanning tree message arrived must be set to forwarding mode if it is not already set
            #    the number of hops to the root (the value in the received packet + 1) must be recorded

            stpmsg = packet.get_header(SpanningTreeMessage)

            log_debug(stpmsg.root)
            log_debug(stpmsg.hops_to_root)
            log_debug(packet[0].src)
            log_debug(packet[0].dst)

            if stpmsg.root < root_id:

                root_id = stpmsg.root
                root_hop_num = stpmsg.hops_to_root + 1
                log_debug(root_hop_num)

                # Set the interface to fwding mode
                fwdModeDict[input_port] = True

                # Record the port of the root stpmsg
                port_root_stpmsg = input_port

                # Forward packets on all ports(except incoming)
                for intf in my_interfaces:
                    if input_port != intf.name:
                        stpPkt = mk_stp_pkt(root_id, root_hop_num, switch_id, packet[0].dst)
                        log_debug ("Flooding packet {} to {}".format(stpPkt, intf.name))
                        net.send_packet(intf.name, stpPkt)
                continue


        # b. If the id in the received packet is the same as the id that the node currently thinks is the root, 
        #    it examines the number of hops to the root value:

        # If the number of hops to the root + 1 is less than the value that the switch has stored, 
        # it sets the interface on which this packet has arrived to forwarding mode (If it is not already set). 
        # The switch should then forward the spanning tree message out all interfaces except the one on which the message arrived, 
        # incrementing the number of hops to the root by 1 prior to forwarding.
        #
            if stpmsg.root == root_id:
                if stpmsg.hops_to_root + 1 < root_hop_num:
                    # Record the port of the root stpmsg
                    port_root_stpmsg = input_port
                    # Set the interface to fwding mode
                    fwdModeDict[input_port] = True
                    root_hop_num = stpmsg.hops_to_root + 1
                    # Forward packets on all ports(except incoming)
                    for intf in my_interfaces:
                        if input_port != intf.name:
                            stpPkt = mk_stp_pkt(root_id, root_hop_num, switch_id, packet[0].dst)
                            log_debug ("Flooding packet {} to {}".format(stpPkt, intf.name))
                            net.send_packet(intf.name, stpPkt)
                    continue

    

        # If the number of hops to the root + 1 is greater than the value that the switch has stored, 
        # just ignore the packet and do nothing

                if stpmsg.hops_to_root + 1 > root_hop_num:
                    continue

        # If the number of hops to the root + 1 equal to the value that the switch has stored, 
        # but is different from the initial port it got this message from, 
        # it should set the interface on which this packet arrived to blocking mode.

                if stpmsg.hops_to_root + 1 == root_hop_num:
                    if port_root_stpmsg != input_port:
                        # Record the port of the root stpmsg
                        port_root_stpmsg = input_port
                        fwdModeDict[input_port] = False
                    continue


        # Lastly, the learning switch forwarding algorithm changes a bit in the context of a spanning tree. 
        # Instead of flooding a frame with an unknown destination Ethernet address out every port 
        # (except the one on which the frame was received), a switch only floods a frame out every port 
        # (again, except the input port) if and only if the interface is in forwarding mode.


        # Determine if table contains entry for src address
        if fwdTable.contain(packet[0].src):
            port_old = fwdTable.get(packet[0].src)

            # Determine if the incoming port for packet the same as
            # the port info in table
            if port_old != input_port:
                # Update port info for the src addr without modifying
                # LRU order
                fwdTable.set(packet[0].src, input_port)

        # When table doesn't contain src address
        # Check if the table is full and add MRU entry
        # This is already implemented in the set() function
        else:
            fwdTable.set(packet[0].src, input_port)

        if packet[0].dst in mymacs:
            log_debug ("Packet intended for me")
            continue
        # Determine if entry for destination exists in table
        if fwdTable.contain(packet[0].dst):
            # Update MRU entry and fwd packet
            dst_port = fwdTable.getNmod(packet[0].dst)
            log_debug ("Flooding packet {} to {}".format(packet, dst_port))
            net.send_packet(dst_port, packet)
        else:
            # Forward packets on all ports(except incoming)
            for intf in my_interfaces:
                if input_port != intf.name and fwdModeDict[input_port] == True:
                    log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                    net.send_packet(intf.name, packet)
        # else:
        #     for intf in my_interfaces:
        #         if input_port != intf.name:
        #             log_debug ("Flooding packet {} to {}".format(packet, intf.name))
        #             net.send_packet(intf.name, packet)
    net.shutdown()
