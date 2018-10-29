#!/usr/bin/python

from scapy.all import *
import pprint
import os
import math
import sys
import db
import time
import func
import random

# init
device = db.get_ap()
#print(device)
xtics = {
	'id': device[0],
	'group_cipher': device[1],
	'protocol': device[2],
	'bssid': device[3],
	'quality': device[4],
	'encryption_key': device[5],
	'pairwise_cipher': device[6],
	'frequency': device[7],
	'rsn_ie': device[8],
	'essid': device[9],
	'bit_rates': device[10],
	'fm': device[11],
	'signal_level': device[12],
	'ie': device[13],
	'authentication_suites': device[14],
	'channel': device[15],
	'mode': device[16],
	'entropy': device[17]
}
entropy = xtics['entropy']

"""
	0 : id
	1 : group_cipher
	2 : protocol
	3 : bssid
	4 : quality
	5 : encryption_key
	6 : pairwise_cipher
	7 : frequency
	8 : rsn_ie
	9 : essid
	10: bit_rates
	11: fm
	12: signal_level
	13: ie
	14: authentication_suites
	15: channel
	16: mode
	17: entropy
"""

iface = 'mon0'

def hopper(iface):
    n = 1
    stop_hopper = False
    while not stop_hopper:
        time.sleep(0.50)
        os.system('iwconfig %s channel %d' % (iface, n))
        dig = int(random.random() * 14)
        if dig != 0 and dig != n:
            n = dig


def packetHandler(pkt):
    #pprint.pprint(pkt)
   
    global start
 
    if pkt.haslayer(Dot11Beacon):
        radioTap = pkt.getlayer(Dot11)
        temp = radioTap.getlayer(Dot11Elt)

        if temp:
            if temp.info == xtics['essid']: # essid
                bssid = radioTap.addr2 # bssid
                channel = str(func.get_channel(temp.payload.payload.info)) # channel

                #print(pkt.show())
                #hexdump(pkt)
                #pkt.psdump('packetFormat')
                #sys.exit()
                # detection rogue
                xtics['bssid'] = xtics['bssid'].lower()
                if (xtics['channel'] == channel) and (xtics['bssid'] == bssid):
                    #print('authorized AP')
                    pass
                else:
                    if xtics['channel'] != channel:
                        xtics['entropy'] -= (-(1.0/14) * math.log(1.0/14, 2))
          
                    if xtics['bssid'] != bssid:
                        xtics['entropy'] -= (-(1.0/14) * math.log(1.0/14, 2))


                    # checking entropy value
                    if xtics['entropy'] < entropy:
                        #print('Rogue detected')
                        #print(bssid + '\t' + channel)
                        execution_time = time.time() - start
                        #print(execution_time)
                        #print('[2] ' + str(start))
                        # log data => aps, exec, memory, entropy
                        db.log(0, execution_time, func.get_usage(), xtics['entropy'])
                        #get_usage()
                        #print('\n')
                        xtics['entropy'] = entropy
    
                        start = time.time()


if __name__ == '__main__':
    #thread = threading.Thread(target=hopper, args=(iface, ), name="ids-hopper")
    #thread.daemon = True
    #thread.start()
    start = time.time()
    while True:
        #print('[1] ' + str(start))
        #sniff(iface=iface, count=20, timeout=3, store=0, prn=packetHandler)
        sniff(iface=iface, prn=packetHandler)
