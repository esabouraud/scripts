#! /bin/python

# On Windows >= XP, get DHCP provided DNS servers, and add custom static DNS servers

import subprocess
import re
import time
import win32serviceutil
import _winreg

if __name__=='__main__':
	IFNAME="Connexion au réseau local"
	STATICDNS = [("bleh.com", "10.23.44.33")]
	
	CMD = "netsh int ipv4 set dnsservers name=\"%s\" source=dhcp"  % IFNAME
	subprocess.call(CMD.decode('utf8').encode('cp1252'))
	
	print "Wait for DHCP to stabilize" 
	time.sleep(2)
	
	CMD = "netsh interface ipv4 show dnsserver \"%s\"" % IFNAME
	print CMD.decode('utf8').encode('cp850')
	proc = subprocess.Popen(CMD.decode('utf8').encode('cp1252'), stdout=subprocess.PIPE)
	RES, ERR = proc.communicate()
	print RES
	dnsaddresses = re.findall('(?:[0-9]{1,3}\.){3}[0-9]{1,3}', RES)
	print dnsaddresses
	
	# dnsaddresses = [dnsaddresses[0], STATICDNS[0]] + dnsaddresses[1:] + STATICDNS[1:]
	# print dnsaddresses
	CMD = "netsh int ipv4 add dnsserver name=\"%s\" 127.0.0.1 index=1" % (IFNAME)
	print CMD.decode('utf8').encode('cp850')
	subprocess.call(CMD.decode('utf8').encode('cp1252'))
	
	unboundservicekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\services\unbound', 0, _winreg.KEY_WOW64_32KEY | _winreg.KEY_READ | _winreg.KEY_QUERY_VALUE | _winreg.KEY_SET_VALUE) 
	unboundservicecmd, type = _winreg.QueryValueEx(unboundservicekey, 'ImagePath')
	print unboundservicecmd
	
	unboundconfmatch = re.match('^.*unbound\.exe.*-c.*"(.*\.conf)".*$', unboundservicecmd)
	print unboundconfmatch.group(1)
	
	unboundconf = open("unboundservice.conf.tmpl").read()
	#print unboundconf
	
	unboundconfnewlines = ['']
	
	for domain, dns in STATICDNS:
		unboundconfnewlines.extend(['forward-zone:', '\tname: "%s"' % domain, '\tforward-addr: "%s"' % dns])
		
	unboundconfnewlines.extend(['', 'forward-zone:', '\tname: "."'])
	for dns in dnsaddresses:
		unboundconfnewlines.append('\tforward-addr: "%s"' % dns)
	unboundconfnewlines.append('')
	
	unboundconf += "\n".join(unboundconfnewlines)
	print unboundconf
	
	# win32serviceutil.RestartService('unbound')
	
	# adding all DNS servers in windows parameter does achieve desired result
	# Algorithm for primary vs secondary selection unclear

	# i = 1
	# for dns in dnsaddresses:
		# CMD = "netsh int ipv4 add dnsserver name=\"%s\" %s index=%d" % (IFNAME, dns, i)
		# print CMD.decode('utf8').encode('cp850')
		# subprocess.call(CMD.decode('utf8').encode('cp1252'))
		# i += 1
