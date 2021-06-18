# Traffic monitoring
In this exercise, you will implement simple traffic monitoring, which lets you count
packets and bytes sent on a given switch port.

In order to do this, we will use P4 counters and a custom control plane written in Python.

## Setting up the environment
Download and run the P4 virtual machine: [P4 Tutorial 2021-06-11.ova](https://drive.google.com/file/d/156lOZxDUAzKV4jL_ROimuxwkubp80R1z)

- Clone this repository and change your working directory
```
$ git clone https://github.com/piotrek-szczygiel/tip-traffic-monitoring.git
$ cd tip-traffic-monitoring/exercises/traffic_monitoring
```

## Topology

For this exercise we will use simple triangle topology consisting of 3 switches and 3 hosts.  
You can inspect specifics of this topology inside the `triangle-topo` directory.

## Information about P4 Counters
In P4 there is an extern type which lets you count various things happening inside your device.  
We will use them to count packets and bytes processed on individual ports of our switches.

### Counter declaration
```P4
extern counter  {
      counter(bit <32> size, CounterType type);
      void count(in bit <32> index);
}
```
### Counter type declaration
```P4
enum CounterType {
    packets,
    bytes,
    packets_and_bytes
}
```

To use counters in your program you need to add this import at the beginning of your `.p4` file:
```P4
#include <v1model.p4>
```
After that you can use them in your P4 code.

## Solving the traffic monitoring exercise

In order to successfully run this exercise you have to fill in `TODO:` sections in source files.


### Exercise 1 - defining the counter in `traffic_monitoring.p4`

```P4
counter(1024, CounterType.packets_and_bytes) traffic_counter;
```

We define counter of size 1024, to match the size of our `ipv4_lpm` table.
Specifing `CounterType` as `packets_and_bytes` means we will be counting both packets and their size.

### Exercise 2 - counting the packets in `traffic_monitoring.p4`

In order for our counter to work, we have to actually invoke it in our program.
Inside of our `ipv4_forward` action we invoke the `count()` method:

```P4
traffic_counter.count((bit<32>) standard_metadata.ingress_port);
```

We use `ingress_port` as an index of our counter, which means that we are counting
packets and bytes going inside individual ports of our device.

### Exercise 3 - modifying the `counter.py` script

You cannot access the counter data from the P4 program - in case of BMV2 switch we are using,
we can create a custom control plane in order to access counter statistics.

There is a `counter.py` script already created which utilizes P4Runtime library in order
to access the counter data.

Inside the `main()` function there is a loop, which prints port usage every 60 seconds.
Modify it to your liking to display statistics e.g. every 5 seconds:

```python
if time % 5 == 0:
    summary(5)
```

### Exercise 4 - constructing the packet in `send.py` script

We will use the `scapy` library to create packets that will simulate the traffic between our hosts.

First, let's create a message that we want to send. You can specify here whatever you want
or just create the `AAAAAA...` string of some random length:

```python
msg = "A" * random.randint(500, 1000)
```

Next we need to create Ethernet frame. Source address will be the `iface_mac` which
holds MAC Address of the sender, and destination will be just a broadcast.

```python
pkt = Ether(src=iface_mac, dst="ff:ff:ff:ff:ff:ff")
```

Now let's create an IP packet and encapsulate it in our Ethernet frame:

```python
pkt = pkt / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152, 65535)) / msg
```

The destination of our packet was passed as a command line argument to our script.
Destination port and source port are arbitrary chosen and you are free to change them
if you feel like it.

## Running the exercise

Now when your P4 program is finished and your `counter.py` and `send.py` scripts
are modified to your liking, you can launch the Mininet environment
and test if everything works fine.

- Start Mininet environment

If your P4 program is correct there should be no errors displayed.
```
$ make run
```

- Run a command from Mininet shell that will send random data every second from h1 to h2:
```
mininet> h1 ./send.py h2
Sending from 08:00:00:00:01:11 to 10.0.2.2

Sent 615 bytes
Sent 642 bytes
Sent 1018 bytes
...
```

- Open and run script that will monitor and display traffic statistics:
```
$ ./counter.py
```

After 5 seconds you should see something similar to this:

```
=== Last 5 seconds summarry ===
s1 1: 4 (2871 bytes)
s1 2: 4 (216 bytes)
s1 3: 0 (0 bytes)
s2 1: 4 (216 bytes)
s2 2: 4 (2871 bytes)
s2 3: 0 (0 bytes)
s3 1: 0 (0 bytes)
s3 2: 0 (0 bytes)
s3 3: 0 (0 bytes)
```

As you can see there is a traffic information about every switch and its port in our topology.

For example switch `s1` received 4 packets on port 1 which were 2871 bytes in total.
