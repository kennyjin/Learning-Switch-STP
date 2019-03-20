# Project 1: Learning Switch with Spanning Tree

This is a project from CS 640, Computer Networks.

## Overview
In this assignment, you are going to implement the core functionalities of an Ethernet learning switch with Spanning Tree using the [Switchyard framework](https://github.com/jsommers/switchyard). An Ethernet switch is a layer 2 device that uses packet switching to receive, process and forward frames to other devices (end hosts, other switches) in the network. A switch has a set of interfaces (ports) through which it sends/receives Ethernet frames. When Ethernet frames arrive on any port, the switch will process the header of the frame to obtain information about the destination host. If the switch knows that the host is reachable through one of its ports, it sends out the frame from the appropriate output port. If it does not know where the host is, it floods the frame out of all ports except the input port.

Spanning Tree (or STP) is a network protocol in Ethernet used to prevent broadcast storms, by converting a physical loop into a logical loop-free topology. This is done by electing a root port in the topology and designating ports as forwarding or blocking, depending on the proximity to the root switch.


## Part 1: Learning Switch
Your task is to implement the logic that is described in the flowchart [here](https://github.com/jsommers/switchyard/blob/master/examples/exercises/learning_switch/learning_switch.rst#ethernet-learning-switch-operation). A more elaborate flowchart has been described in the FAQ section. As it is described in the last paragraph of the "Ethernet Learning Switch Operation" section, your switch will also handle the frames that are intended for itself and the frames whose Ethernet destination address is the broadcast address FF:FF:FF:FF:FF:FF.

In addition to these, you will also implement a mechanism to purge the outdated/stale entries from the forwarding table. This will allow your learning switch to adapt to changes in the network topology.

You will implement the following mechanism:

* Remove the least recently used (LRU) entry from the forwarding table. For this functionality assume that your table can only hold 5 entries at a time. If a new entry comes and your table is full, you will remove the entry that has not been matched with a Ethernet frame destination address for the longest time.
You will implement this mechanisms in a Python file named myswitch_lru.py.

 

**NOTE**: There is an example of a switch without learning implemented in  switchyard-master/examples/exercises/learning_switch/ which will likely be useful to get you started.

 

Also please keep an eye on the FAQ section below which will be updated with information regarding most common doubts that arise during implementation.


## Part 2: Spanning Tree implementation
For the second part of the assignment you will build on top of your learning switch implementation. STP packets will be handled in a separate code path whereas the other packets will continue as per the behaviour of the learning switch. Create a copy of the above file and name it as myswitch_stp.py. You will be implementing a simplified version of the Spanning Tree Protocol for the purpose of this assignment. We have modified the problem description from [here](https://github.com/jsommers/switchyard/blob/master/examples/exercises/learning_switch/learning_switch.rst#implement-a-simplified-spanning-tree-computation-algorithm) to suite our requirements as described below. (NOTE: This is not the actual STP working but a simplified version which can be implemented within the restrictions of the framework capabilities.)

If you attempt to run your switch on multiple nodes within a virtual network using Mininet, and if there is a physical loop in the network, you will observe that packets will circulate infinitely. Oops. An interesting and challenging extension to the learning switch is to implement a simplified spanning tree computation algorithm. Once the spanning tree is computed among switches in the network, traffic will only be forwarded along links that are part of the spanning tree, thus eliminating the loop and preventing packets from circulating infinitely.

To implement a spanning tree computation, you'll need to do the following:

1. Add to your switch the notion of an id, which can just be an integer (or even a string). The point is that each switch will need its own unique id, and there should be a simple way to compare ids. (NOTE: For our implementation the ID of the switch will be equal to the smallest MAC address among all it’s ports MAC addresses.)
2. Create a new packet header type that includes two attributes: the id of the root node in the spanning tree, and the number of observed hops to the root. (NOTE: For this part of the assignment you can refer to API example given here (Links to an external site.)Links to an external site.. We have already packaged the implementation and given it in the starter code under spanningtreemessage.py. Just import that in your myswitch_stp.py). The source and destination MACs in the Ethernet header can be anything as we are not going to learn any MAC table information from STP packets.
3. Add a capability to each switch so that when it starts up, it floods out spanning tree packets to determine and/or find out what node is the root. Each switch needs to store a few things: the id of the current root (which is initialized to the switch's own id), the number of hops to the root (initialized to 0), and the time at which the last spanning tree message was received. Each non-root node also needs to remember which interface on which spanning tree message from the perceived root arrives.
4. Only root nodes generate STP packets periodically. Initially, a node assumes that it is the root. These packets are initialized with the switch's own id and 0 as the number of hops to the root. The root note should emit new spanning tree packets every 2 seconds. All the interface of the router will be in forwarding mode.
5. When a node receives a spanning tree packet it examines the root attribute:
    * If the id in the received packet is smaller than the id that the node currently thinks is the root, the id in the received packet becomes the new root. The node should then forward the packet out all interfaces except for the one on which the packet was received. Prior to forwarding, the number of hops to the root should be incremented by 1. The interface on which the spanning tree message arrived must be set to forwarding mode if it is not already set, and the number of hops to the root (the value in the received packet + 1) must be recorded.
    * If the id in the received packet is the same as the id that the node currently thinks is the root, it examines the number of hops to the root value:
    * If the number of hops to the root + 1 is less than the value that the switch has stored, it sets the interface on which this packet has arrived to forwarding mode (If it is not already set). The switch should then forward the spanning tree message out all interfaces except the one on which the message arrived, incrementing the number of hops to the root by 1 prior to forwarding.
    * If the number of hops to the root + 1 is greater than the value that the switch has stored, just ignore the packet and do nothing
    * If the number of hops to the root + 1 equal to the value that the switch has stored, but is different from the initial port it got this message from, it should set the interface on which this packet arrived to blocking mode.
    * Lastly, the learning switch forwarding algorithm changes a bit in the context of a spanning tree. Instead of flooding a frame with an unknown destination Ethernet address out every port (except the one on which the frame was received), a switch only floods a frame out every port (again, except the input port) if and only if the interface is in forwarding mode.

## Testing your code
Once you develop your learning switch, you should test the correctness of your implementation. Switchyard allows you to write scenarios to test your implementation. You can also find a simple test scenario in switchyard/examples/hubtests.py. Once you understand and get comfortable with the framework, make sure that you test your switch implementations meticulously. Do not forget to consider corner cases. Make sure that your entry purging mechanisms work as expected.

Once you prepare your test scenario, you can compile it as follows:

```
./swyard.py -c mytestscenario.py
```
**Note**: You should type in the path of swyard.py to run the tests. The path should be where is switchyard is installed.


To run the test scenario with your switch implementation:

```
./swyard.py -t mytestscenario.srpy myswitchimplementation.py
```

You can find more detailed information on compiling test scenarios and running in the test environment in the Switchyard documentation.

***(Optional)*** In addition to these, you should also try running your switch in Mininet. You can find more information on this [here](https://github.com/jsommers/switchyard/blob/master/examples/exercises/learning_switch/learning_switch.rst#testing-and-deploying-your-switch).

**NOTE**: LRU implementation can be tested using the compiled code. But for testing the STP implementation directly pass the python file.

```
./swyard.py -t testfile.py myswitch_stp.py
```

## Development notes
We are providing you with a Ubuntu 14.04 (64-bit) VM image for this assignment. This image has Switchyard, Mininet and Wireshark installed so you do not need to worry about setting up the environment.

## FAQs
1. Q: How do the entry removal mechanisms work? 

   A: [Flow chart for LRU](http://pages.cs.wisc.edu/~karthikc/CS640S19/P1/lru_flow.jpg)

2. Q. What MAC addresses should STP packets contain when being flooded or forwarded?

    A. STP packets are generated at the node itself, so whenever a STP packet is to be sent, it should be sent with src MAC of the node (for convenience hard-code the src mac to the ethernet address of eth0  and destination should be broadcast always: "ff:ff:ff:ff:ff:ff")

