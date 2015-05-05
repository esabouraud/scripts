#! /bin/python

# On Windows >= XP, get DHCP provided DNS servers, and add custom static DNS servers

import subprocess
import re
import time

if __name__=='__main__':
	IFNAME="Connexion au réseau local"
	STATICDNS = ["10.23.44.33"]
	
	CMD = "netsh int ipv4 set dnsservers name=\"%s\" source=dhcp"  % IFNAME
	subprocess.call(CMD.decode('utf8').encode('cp1252'))
	
	print "Wait for DHCP to stabilize" 
	time.sleep(5)
	
	CMD = "netsh interface ipv4 show dnsserver \"%s\"" % IFNAME
	print CMD.decode('utf8').encode('cp850')
	proc = subprocess.Popen(CMD.decode('utf8').encode('cp1252'), stdout=subprocess.PIPE)
	RES, ERR = proc.communicate()
	print RES
	dnsaddresses = re.findall("(?:[0-9]{1,3}\.){3}[0-9]{1,3}", RES)
	print dnsaddresses
	
	dnsaddresses = [dnsaddresses[0], STATICDNS[0]] + dnsaddresses[1:] + STATICDNS[1:]
	print dnsaddresses
	# i = 1
	# for dns in dnsaddresses:
		# CMD = "netsh int ipv4 add dnsserver name=\"%s\" %s index=%d" % (IFNAME, dns, i)
		# print CMD.decode('utf8').encode('cp850')
		# subprocess.call(CMD.decode('utf8').encode('cp1252'))
		# i += 1
