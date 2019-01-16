# !/usr/bin/python

"""
Task 1: Implementation of the experiment described in the paper with title: 
"From Theory to Experimental Evaluation: Resource Management in Software-Defined Vehicular Networks"
http://ieeexplore.ieee.org/document/7859348/
"""

import os
import time
import matplotlib.pyplot as plt
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, OVSKernelAP
from mininet.link import TCLink
from mininet.log import setLogLevel, debug
from mininet.cli import CLI

import sys
gnet=None

# Store metrics here
c0_throughput0 = 'c0_throughput0.data'          # car0 throughput phase 1
client_throughput0 = 'client_throughput0.data'	# client throughput phase 1
c0_throughput1 = 'c0_throughput1.data'          # car0 throughput phase 2
client_throughput1 = 'client_throughput1.data'  # client throughput phase 2
c0_throughput2 = 'c0_throughput2.data'          # car0 throughput phase 3
client_throughput2 = 'client_throughput2.data'  # client throughput phase 3

c0_latency0 = 'c0_latency0.data'		# car0 latency phase 1
c3_latency0 = 'c3_latency0.data'		# car3 latency phase 1
c0_latency1 = 'c0_latency1.data'		# car0 latency phase 2
c0_latency2 = 'c0_latency2.data'		# car0 latency phase 3

c0c3_iperf0 = 'c0c3_iperf0.data'            # car0-car3 phase 1
c3client_iperf0 = 'c3client_iperf0.data'	# car3-client phase 1
c0client_iperf1 = 'c0client_iperf1.data'	# car0-client phase 2
c0client_iperf2 = 'c0client_iperf2.data'	# car0-client phase 3

# Implement the graphic function in order to demonstrate the network measurements
def graphic():
    plt.clf()	# clear current figure

    # Throughput
    for j in range(0,3):

	    # open "client_throughputX.data" file in current directory, in read mode - store lines in variable
        f1 = open('./' + 'client_throughput' + str(j) + '.data', 'r')	
        f1_lines = f1.readlines()
        f1.close()

	    # open "c0_throughput.data" file - store lines in variable
        f2 = open('./' + 'c0_throughput' + str(j) + '.data', 'r')
        f2_lines = f2.readlines()
        f2.close()

        rx = []
        d_rx = []
        tx = []
        d_tx = []
        time_rx = []
        time_tx = []

        i = 0
	    # read line by line
        for x in f1_lines:    
            p = x.split()	    # p: list of all the words in each line, seperation by space
                                # RX bytes: total bytes received through the interface
            t = p[1].split(':')	# take all words in 2nd element of p, seperated by :
            rx.append(int(t[1]))# fill rx with the 2nd element of the 2nd element of p
            if len(rx) > 1:
                d_rx.append(rx[i] - rx[i - 1])	#store the differences between subsequent rxes, in d_rx
            i += 1

        i = 0
        # read line by line
        for x in f2_lines:    
            p = x.split()
				                # TX bytes: total bytes transmitted through the interface
            t = p[5].split(':') # take all words in 6th element of p, seperated by :
            tx.append(int(t[1]))# fill tx with the 2nd element of the 6th element of p
            if len(tx) > 1:
                d_tx.append(tx[i] - tx[i - 1])	#store the differences between subsequent txes, in d_tx
            i += 1

        # create time axes
        i = 0
        for x in range(len(d_tx)):    
            time_tx.append(i)
            i = i + 0.5

        i = 0
        for x in range(len(d_rx)):    
            time_rx.append(i)
            i = i + 0.5
        
        fig = plt.figure(figsize=(16,6))    # start a figure
        g = fig.add_subplot(121)            # add a 1st subfigure
        g.plot(time_rx, d_rx)				
        plt.xlabel('Time')
        plt.ylabel('Bytes')
        plt.ylim([-100, 100000])
        plt.title('Client - RX')

        b = fig.add_subplot(122)		    # add a 2nd subfigure
        b.plot(time_tx, d_tx)
        plt.xlabel('Time')
        plt.ylabel('Bytes')
        plt.ylim([-100, 100000])
        plt.title('Car0 - TX')

        plt.savefig('Plot_Throughput_phase' + str(j) + '.png')
        plt.clf()

    # Latency
    for j in range(0,3):
        f1 = open('./' + 'c0_latency' + str(j) + '.data', 'r')
        f1_lines = f1.readlines()
        f1.close()

        lat = []
        time = []
        i = 1
        fl =  len(f1_lines) - 5
        while i <= fl:  
            x = f1_lines[i]  
            p = x.split()
            t = p[6].split('=')
            lat.append(float(t[1]))
            i = i +1
         
        if j ==0:		# calculations for phase 1
            f2 = open('./' + 'c3_latency' + str(j) + '.data', 'r')
            f2_lines = f2.readlines()
            f2.close()
            lat2 = []
            i = 1
            fl2 =  len(f2_lines) - 5
            while i <= fl2:  
                x = f2_lines[i]  
                p = x.split()
                t = p[6].split('=')
                lat2.append(float(t[1]))
                i = i + 1
            total = []
            total = [sum(i) for i in zip(lat,lat2)]
            i = 1
            for x in range(len(total)):    
                time.append(i)
                i = i + 1
            plt.plot(time,total)
            plt.xlabel('Time (ms)')
            plt.ylabel('Ping number')
            plt.savefig('Plot_Latency_phase' + str(j) + '.png')
            plt.clf()
        else:			# calculations for phases 2-3
            i = 1
            for x in range(len(lat)):    
                time.append(i)
                i = i + 1
            plt.plot(time,lat)
            plt.xlabel('Time (ms)')
            plt.ylabel('Ping number')
            plt.savefig('Plot_Latency_phase' + str(j) + '.png')
            plt.clf()

    # Jitter and Packet Loss
    for j in range(0,3):
        time_jitter = []
        time_loss = []
        jitter = []
        loss =[]
        if j ==0:		# calculations for phase 1
            f1 = open('./' + c0c3_iperf0 , 'r')
            f1_lines = f1.readlines()
            f1.close()
            f2 = open('./' + c3client_iperf0, 'r')
            f2_lines = f2.readlines()
            f2.close()
            i = 7
            while i < len(f1_lines):
                x = f1_lines[i] 
                p = x.split()
                l = len(p)
                if l > 12:
                    t = p[l-1].split('%')
                    t2 = t[0].split('(')
                    loss.append(float(t2[1]))
                    jitter.append(float(p[l-5]))
                i = i +1
            jitter1 = []
            loss1 = []
            i = 7
            while i < len(f2_lines):
                x = f2_lines[i] 
                p = x.split()
                l = len(p)
                if l > 12:
                    t = p[l-1].split('%')
                    t2 = t[0].split('(')
                    loss1.append(float(t2[1]))
                    jitter1.append(float(p[l-5]))
                i = i +1
            total_jitter = []
            total_loss = []
            total_jitter = [sum(i) for i in zip(jitter,jitter1)]
            total_loss = [sum(i) for i in zip(loss,loss1)]
            i = 1
            for x in range(len(total_loss)):    
                time_loss.append(i)
                i = i + 1
            i = 1
            for x in range(len(total_jitter)):    
                time_jitter.append(i)
                i = i + 1
            plt.plot(time_jitter,total_jitter)
            plt.xlabel('Iperf number')
            plt.ylabel('Jitter (ms)')
            plt.savefig('Plot_Jitter_phase0.png')
            plt.clf()
            plt.plot(time_loss,total_loss)
            plt.xlabel('Iperf number')
            plt.ylabel('Packet Loss (%)')
            plt.savefig('Plot_PacketLoss_phase0.png')
            plt.clf()
        else:			# calculations for phases 2-3
            f1 = open('./' + 'c0client_iperf' + str(j) + '.data', 'r')
            f1_lines = f1.readlines()
            f1.close()
            i = 7
            while i < len(f1_lines):
                x = f1_lines[i] 
                p = x.split()
                l = len(p)
                if l > 12:
                    t = p[l-1].split('%')
                    t2 = t[0].split('(')
                    loss.append(float(t2[1]))
                    jitter.append(float(p[l-5]))
                i = i + 1
            i = 1
            for x in range(len(loss)):    
                time_loss.append(i)
                i = i + 1
            i = 1
            for x in range(len(jitter)):    
                time_jitter.append(i)
                i = i + 1
            plt.plot(time_jitter,jitter)
            plt.xlabel('Iperf number')
            plt.ylabel('Jitter (ms)')
            plt.savefig('Plot_Jitter_phase' + str(j) + '.png')
            plt.clf()
            plt.plot(time_loss,loss)
            plt.xlabel('Iperf number')
            plt.ylabel('Packet Loss (%)')
            plt.savefig('Plot_PacketLoss_phase' + str(j) + '.png')
            plt.clf()
    print "ready"

def apply_experiment(car,client,switch):
    
    taskTime = 20

    #time.sleep(2)
    print "Applying first phase"

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=output:4')  # eNodeB1 to client
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:1')  # client to eNodeB1
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=drop')      # eNodeB2 drop
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=drop')      # RSU1 drop

    car[0].cmd('ip route add 200.0.10.2 via 200.0.10.50')		
    client.cmd('ip route add 200.0.10.100 via 200.0.10.150')	 

	# Uncomment to pause on console
    # print "*** Running CLI"
    # CLI(gnet)

    # car0-car3 latency
    car[0].cmd('ping 192.168.1.7  -c 20 >> %s &' % c0_latency0)	# latency phase 1
    car[3].cmd('ping 200.0.10.2  -c 20 >> %s &' % c3_latency0)	

    # car0-car3 iperf
    car[3].cmd('iperf -s -u -i 1 >> %s &' % c0c3_iperf0)        # iperf metrics phase 1
    car[0].cmd('iperf -c 192.168.1.7 -u -i 1 -t 20')

    # car3-client iperf
    client.cmd('iperf -s -u -i 1 >> %s &' % c3client_iperf0)	#-s: iperf in server mode, -u=use UDP not TCP 
    car[3].cmd('iperf -c 200.0.10.2 -u -i 1 -t 20')		        #-i interval=1, -t=transmit for 20 sec, to client
                                                                #-c: accept connections only to this host
    # car0-client throughput
    timeout = time.time() + taskTime
    currentTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - currentTime >= i:		# store RX and TX data phase 1
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> %s' % c0_throughput0)
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> %s' % client_throughput0)
            i += 0.5
    
    print "Moving nodes"
    car[0].moveNodeTo('150,100,0')
    car[1].moveNodeTo('120,100,0')
    car[2].moveNodeTo('90,100,0')
    car[3].moveNodeTo('70,100,0')

    #time.sleep(2)
    print "Applying second phase"

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')	    # eNodeB1 drop
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')	# eNodeB2 to client
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=output:4')	# RSU1 to client
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2,3')# client to eNodeB2 & RSU1

    car[0].cmd('ip route del 200.0.10.2 via 200.0.10.50')       # delete previous phase's routings
    client.cmd('ip route del 200.0.10.100 via 200.0.10.150')

    # print "*** Running CLI"
    # CLI(gnet)

    # car0 latency
    car[0].cmd('ping 200.0.10.2  -c 20 >> %s &' % c0_latency1)	# latency  phase 2

    # car0-client iperf
    client.cmd('iperf -s -u -i 1 >> %s &' % c0client_iperf1)	# iperf metrics phase 2
    car[0].cmd('iperf -c 200.0.10.2 -u -i 1 -t 20')

    # car0-client throughput
    timeout = time.time() + taskTime
    currentTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - currentTime >= i:        # store RX and TX data phase 2
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> %s' % c0_throughput1)
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> %s' % client_throughput1)
            i += 0.5

    print "Moving nodes"
    car[0].moveNodeTo('190,100,0')
    car[1].moveNodeTo('150,100,0')
    car[2].moveNodeTo('120,100,0')
    car[3].moveNodeTo('90,100,0')

    #time.sleep(2)
    print "Applying third phase"

    os.system('ovs-ofctl mod-flows switch in_port=1,actions=drop')    # eNodeB1 drop
    os.system('ovs-ofctl mod-flows switch in_port=3,actions=drop')    # RSU1 drop
    os.system('ovs-ofctl mod-flows switch in_port=2,actions=output:4')# eNodeB2 to client
    os.system('ovs-ofctl mod-flows switch in_port=4,actions=output:2')# client to eNodeB2

    #print "*** Running CLI"
    #CLI(gnet)

    # car0 latency
    car[0].cmd('ping 200.0.10.2  -c 20 >> %s &' % c0_latency2)	# latency phase 3

    # car0-client iperf
    client.cmd('iperf -s -u -i 1 >> %s &' % c0client_iperf2)	# iperf metrics phase 3
    car[0].cmd('iperf -c 200.0.10.2 -u -i 1 -t 20')

    # car0-client throughput
    timeout = time.time() + taskTime
    currentTime = time.time()
    i = 0
    while True:
        if time.time() > timeout:
            break;
        if time.time() - currentTime >= i:		# store RX and TX data phase 3
            car[0].cmd('ifconfig bond0 | grep \"bytes\" >> %s' % c0_throughput2)
            client.cmd('ifconfig client-eth0 | grep \"bytes\" >> %s' % client_throughput2)
            i += 0.5


def topology():
    "Create a network."
    net = Mininet(controller=Controller, link=TCLink, switch=OVSKernelSwitch, accessPoint=OVSKernelAP)
    global gnet
    gnet = net

    print "*** Creating nodes"
    car = []
    stas = []
    for x in range(0, 4):
        car.append(x)
        stas.append(x)
    for x in range(0, 4):
        car[x] = net.addCar('car%s' % (x), wlans=2, ip='10.0.0.%s/8' % (x + 1), \
        mac='00:00:00:00:00:0%s' % x, mode='b')

    
    eNodeB1 = net.addAccessPoint('eNodeB1', ssid='eNodeB1', dpid='1000000000000000', mode='ac', channel='1', position='80,75,0', range=60)
    eNodeB2 = net.addAccessPoint('eNodeB2', ssid='eNodeB2', dpid='2000000000000000', mode='ac', channel='6', position='180,75,0', range=70)
    rsu1 = net.addAccessPoint('rsu1', ssid='rsu1', dpid='3000000000000000', mode='g', channel='11', position='140,120,0', range=40)
    c1 = net.addController('c1', controller=Controller)
    client = net.addHost ('client')
    switch = net.addSwitch ('switch', dpid='4000000000000000')

    net.plotNode(client, position='125,230,0')
    net.plotNode(switch, position='125,200,0')

    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    print "*** Creating links"
    net.addLink(eNodeB1, switch)
    net.addLink(eNodeB2, switch)
    net.addLink(rsu1, switch)
    net.addLink(switch, client)

    print "*** Starting network"
    net.build()
    c1.start()
    eNodeB1.start([c1])
    eNodeB2.start([c1])
    rsu1.start([c1])
    switch.start([c1])

    for sw in net.vehicles:
        sw.start([c1])

    i = 1
    j = 2
    for c in car:
        c.cmd('ifconfig %s-wlan0 192.168.0.%s/24 up' % (c, i))
        c.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (c, i))
        c.cmd('ip route add 10.0.0.0/8 via 192.168.1.%s' % j)
        i += 2
        j += 2

    i = 1
    j = 2
    for v in net.vehiclesSTA:
        v.cmd('ifconfig %s-eth0 192.168.1.%s/24 up' % (v, j))
        v.cmd('ifconfig %s-mp0 10.0.0.%s/24 up' % (v, i))
        v.cmd('echo 1 > /proc/sys/net/ipv4/ip_forward')
        i += 1
        j += 2

    for v1 in net.vehiclesSTA:
        i = 1
        j = 1
        for v2 in net.vehiclesSTA:
            if v1 != v2:
                v1.cmd('route add -host 192.168.1.%s gw 10.0.0.%s' % (j, i))
            i += 1
            j += 2

    client.cmd('ifconfig client-eth0 200.0.10.2')
    net.vehiclesSTA[0].cmd('ifconfig car0STA-eth0 200.0.10.50')

    car[0].cmd('modprobe bonding mode=3')
    car[0].cmd('ip link add bond0 type bond')
    car[0].cmd('ip link set bond0 address 02:01:02:03:04:08')
    car[0].cmd('ip link set car0-eth0 down')
    car[0].cmd('ip link set car0-eth0 address 00:00:00:00:00:11')
    car[0].cmd('ip link set car0-eth0 master bond0')
    car[0].cmd('ip link set car0-wlan0 down')
    car[0].cmd('ip link set car0-wlan0 address 00:00:00:00:00:15')
    car[0].cmd('ip link set car0-wlan0 master bond0')
    car[0].cmd('ip link set car0-wlan1 down')
    car[0].cmd('ip link set car0-wlan1 address 00:00:00:00:00:13')
    car[0].cmd('ip link set car0-wlan1 master bond0')
    car[0].cmd('ip addr add 200.0.10.100/24 dev bond0')
    car[0].cmd('ip link set bond0 up')

    car[3].cmd('ifconfig car3-wlan0 200.0.10.150')

    client.cmd('ip route add 192.168.1.8 via 200.0.10.150')
    client.cmd('ip route add 10.0.0.1 via 200.0.10.150')

    net.vehiclesSTA[3].cmd('ip route add 200.0.10.2 via 192.168.1.7')
    net.vehiclesSTA[3].cmd('ip route add 200.0.10.100 via 10.0.0.1')
    net.vehiclesSTA[0].cmd('ip route add 200.0.10.2 via 10.0.0.4')

    car[0].cmd('ip route add 10.0.0.4 via 200.0.10.50')
    car[0].cmd('ip route add 192.168.1.7 via 200.0.10.50')
    car[0].cmd('ip route add 200.0.10.2 via 200.0.10.50')
    car[3].cmd('ip route add 200.0.10.100 via 192.168.1.8')

    """plot graph"""
    net.plotGraph(max_x=250, max_y=250)

    net.startGraph()

    # Stream video using VLC 
    car[0].cmdPrint("vlc -vvv bunnyMob.mp4 --sout '#duplicate{dst=rtp{dst=200.0.10.2,port=5004,mux=ts},dst=display}' :sout-keep &")
    client.cmdPrint("vlc rtp://@200.0.10.2>:5004 &")

    car[0].moveNodeTo('95,100,0')
    car[1].moveNodeTo('80,100,0')
    car[2].moveNodeTo('65,100,0')
    car[3].moveNodeTo('50,100,0')

    os.system('ovs-ofctl del-flows switch')

    time.sleep(3)

    apply_experiment(car,client,switch)

    graphic()

    # kills all the xterms that have been opened
    os.system('pkill xterm')

    print "*** Running CLI"
    CLI(net)

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    try:
        topology()
    except:
        type = sys.exc_info()[0]
        error = sys.exc_info()[1]
        traceback = sys.exc_info()[2]
        print ("Type: %s" % type)
        print ("Error: %s" % error)
        print ("Traceback: %s" % traceback)
        if gnet != None:
            gnet.stop()
        else:
            print "No network was created..."
