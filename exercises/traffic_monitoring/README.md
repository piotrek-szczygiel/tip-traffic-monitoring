# Traffic monitoring
In this exercise, you will implement type of traffic monitoring where you can display your network status depending on time window you define.
To do this we will use counters with custom Control Plane.


## How to run the excercise:

1. In your shell run:
```
make run
```

2. You should now see a Mininet command prompt. Now please run command that will simulate traffic between two hosts:
```
h1 ./send.py h2
```
This command will send random data every 5 seconds from h1 to h2.

3. Open second terminal and run:
```
./counter.py
```

This command will start monitoring function which displays data transfered between hosts in time window defined inside.
## Theory
In P4 there are extern types, functions and objects. They are all defined in the architecture file description [v1model.p4](https://github.com/p4lang/p4c/blob/master/p4include/v1model.p4).
### To declare counter in P4 you need to define extern type:
```P4
extern counter  {
      counter ( bit <32> size ,  CounterType  type );
      void  count ( in  bit <32> index ) ;
}
```
### The granularity of each counter, packets, bytes or both, can be specified using the following enum:
```P4
enum CounterType {
    packets,
    bytes,
    packets_and_bytes
}
```
The v1model already includes the declarations from above, you should have it accessible on your system if you installed P4 correctly.
You just need to add import at the beginning of .p4 file:
```P4
#include <v1model.p4>
```
After that you can use them in your P4 code.

### Custom Control Plane to read counters state
In file [counter.py](./counter.py) you can see the control plane.
You can observe that there are functions to read the counter state like *get_packets_and_bytes()* that reads packet and bytes data from counter which suggests the type of counter you should define. 

Function *packets_and_bytes()* uses that code to read that from counter with defined name - *traffic_counter*.
```python
def get_packets_and_bytes(p4info_helper, sw, counter_name, index):
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            return counter.data.packet_count, counter.data.byte_count

def packets_and_bytes(switch, port):
      return get_packets_and_bytes(p4info_helper, switch, "MyIngress.traffic_counter", port)
```
Each switch has method to read data from counter: *ReadCounters(...)* - which returns data that counter provides.

## Excercise:

#### Task 1: Define counter in [traffic_monitoring.p4](./traffic_monitoring.p4) and call proper method.
#### Task 2: Change P4 code so that only valid packets will be counted.
#### Task 3: Change [counter.py](./counter.py) to support other types of window besides 60 seconds.

Code above will work correctly when you will fill properly all TODOs left in the code of [counter.py](./counter.py) and [traffic_monitoring.p4](./traffic_monitoring.p4) 

You don't have to make any changes to your topology, but if you want to - you have to also change it in Control Plane.
If you encounter any probles you can help yourself with files in soultion folder.
