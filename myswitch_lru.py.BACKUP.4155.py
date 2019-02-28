'''
Ethernet learning switch in Python.

Note that this file currently has the code to implement a "hub"
in it, not a learning switch.  (I.e., it's currently a switch
that doesn't learn.)
'''
from switchyard.lib.userlib import *
<<<<<<< HEAD
=======
import collections
>>>>>>> push

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



def main(net):
    my_interfaces = net.interfaces() 
    mymacs = [intf.ethaddr for intf in my_interfaces]
<<<<<<< HEAD

=======
>>>>>>> push
    # Set up the forwarding table
    TABLE_CAPACITY = 5
    fwdTable = FwdTable(TABLE_CAPACITY)

    while True:
        try:
            timestamp,input_port,packet = net.recv_packet()
        except NoPackets:
            continue
        except Shutdown:
            return

        # Apparently the LRU Cache data structure is needed.
        # Each entry in the table is in the form of (src, port)
        # src, in this case, is packet[0].src
        # port, in this case, is input_port

        log_debug ("In {} received packet {} on {}".format(net.name, packet, input_port))

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

<<<<<<< HEAD
=======
        if packet[0].dst in mymacs:
            log_debug ("Packet intended for me")
            continue
>>>>>>> push
        # Determine if entry for destination exists in table
        if fwdTable.contain(packet[0].dst):
            # Update MRU entry and fwd packet
            dst_port = fwdTable.getNmod(packet[0].dst)
            log_debug ("Flooding packet {} to {}".format(packet, dst_port))
            net.send_packet(dst_port, packet)
        else:
            # Forward packets on all ports(except incoming)
            for intf in my_interfaces:
                if input_port != intf.name:
                    log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                    net.send_packet(intf.name, packet)

                




<<<<<<< HEAD
        if packet[0].dst in mymacs:
            log_debug ("Packet intended for me")
        else:
            for intf in my_interfaces:
                if input_port != intf.name:
                    log_debug ("Flooding packet {} to {}".format(packet, intf.name))
                    net.send_packet(intf.name, packet)
=======
        
        # else:
        #     for intf in my_interfaces:
        #         if input_port != intf.name:
        #             log_debug ("Flooding packet {} to {}".format(packet, intf.name))
        #             net.send_packet(intf.name, packet)
>>>>>>> push
    net.shutdown()
