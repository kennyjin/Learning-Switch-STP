#!/usr/bin/env python3
from switchyard.lib.userlib import *

def mkpkt(src, dst):
    testpkt = Ethernet() + IPv4() + ICMP()
    testpkt[0].src = src
    testpkt[0].dst = dst
    return testpkt

def create_scenario():
    s = TestScenario("LRU switch topology update test")
    s.add_interface('eth1', '10:00:00:00:00:01')
    s.add_interface('eth2', '10:00:00:00:00:02')
    s.add_interface('eth3', '10:00:00:00:00:03')
    s.add_interface('eth4', '10:00:00:00:00:04')
    s.add_interface('eth5', '10:00:00:00:00:05')
    s.add_interface('eth6', '10:00:00:00:00:06')
    s.add_interface('eth7', '10:00:00:00:00:07')

    #case1: broadcasting
    testpkt = mkpkt( "30:00:00:00:00:01", "ff:ff:ff:ff:ff:ff")
    s.expect(PacketInputEvent("eth1", testpkt, display=Ethernet), "packet from eth1")
    s.expect(PacketOutputEvent("eth2", testpkt, "eth3", testpkt, "eth4", testpkt, "eth5", testpkt,"eth6", testpkt,"eth7", testpkt, display=Ethernet), "broadcast: flood all but incoming ports")

    #case2: packet for the switch get dropped
    testpkt = mkpkt( "30:00:00:00:00:01", "10:00:00:00:00:01")
    s.expect(PacketInputEvent("eth1", testpkt, display=Ethernet), "packet from eth1")

    #case3: before learning: flood
    testpkt = mkpkt( "30:00:00:00:00:01", "30:00:00:00:00:02")
    s.expect(PacketInputEvent("eth1", testpkt, display=Ethernet), "packet from eth1")
    s.expect(PacketOutputEvent("eth2", testpkt, "eth3", testpkt, "eth4", testpkt, "eth5", testpkt,"eth6", testpkt,"eth7", testpkt, display=Ethernet), "before learning flood eth2-7")

    #case4: after learning send to port
    testpkt = mkpkt( "30:00:00:00:00:02", "30:00:00:00:00:01")
    s.expect(PacketInputEvent("eth2", testpkt, display=Ethernet), "packet from eth2")
    s.expect(PacketOutputEvent("eth1", testpkt, display=Ethernet), "After learning & before TO, only send to eth1")

    #case 5: full table kicks LRU
    testpkt = mkpkt( "30:00:00:00:00:01", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth1", testpkt, display=Ethernet), "send the packet from eth1")

    testpkt = mkpkt( "30:00:00:00:00:02", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth2", testpkt, display=Ethernet), "send the packet from eth2")

    testpkt = mkpkt( "30:00:00:00:00:03", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth3", testpkt, display=Ethernet), "send the packet from eth3")

    testpkt = mkpkt( "30:00:00:00:00:04", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth4", testpkt, display=Ethernet), "send the packet from eth4")

    testpkt = mkpkt( "30:00:00:00:00:05", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth5", testpkt, display=Ethernet), "send the packet from eth5")
    #cache shuold be full now, and eth2 is the LRU
    testpkt = mkpkt( "30:00:00:00:00:06", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth6", testpkt, display=Ethernet), "send the packet from eth6")
    # 02's mapping should be kicked
    testpkt = mkpkt( "30:00:00:00:00:06", "30:00:00:00:00:02")
    s.expect(PacketInputEvent("eth6", testpkt, display=Ethernet), "send the packet from eth6")
    s.expect(PacketOutputEvent("eth1", testpkt, "eth2", testpkt, "eth3", testpkt, "eth4", testpkt,"eth5", testpkt,"eth7", testpkt, display=Ethernet), "eth1 should be out. flood to ports eth1-5 and eth7")

    #case 6: topology change doesn't change freshness
    # 01's mapping should be the LRU
    testpkt = mkpkt( "30:00:00:00:00:01", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth2", testpkt, display=Ethernet), "change topology so src=01 comes from eth2") 
    # 01's mapping should be kicked
    testpkt = mkpkt( "30:00:00:00:00:07", "10:00:00:00:00:01")      #send to switch to simply drop the packet
    s.expect(PacketInputEvent("eth7", testpkt, display=Ethernet), "send the packet from eth7") 
    # packets for 01 should be flooded
    testpkt = mkpkt( "30:00:00:00:00:06", "30:00:00:00:00:01")
    s.expect(PacketInputEvent("eth6", testpkt, display=Ethernet), "send the packet from eth6")
    s.expect(PacketOutputEvent("eth1", testpkt, "eth2", testpkt, "eth3", testpkt, "eth4", testpkt,"eth5", testpkt,"eth7", testpkt, display=Ethernet), "eth1 should be out. flood to ports eth1-5 and eth7")
    return s

# the name scenario here is required --- the Switchyard framework will
# explicitly look for an object named scenario in the test description file.
scenario = create_scenario()