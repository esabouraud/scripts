#! /bin/python

# On Windows >= XP, get DHCP provided DNS servers, and add custom static DNS servers

import subprocess
import re
import time
import win32serviceutil
import _winreg
import argparse
import ast
import logging

def getDNSfromDHCP(IFNAME):
	logging.info("Set interface \"%s\" DNS source as DHCP and wait." % IFNAME.decode('utf8').encode('850'))
	
	CMD = "netsh int ipv4 set dnsservers name=\"%s\" source=dhcp"  % IFNAME
	subprocess.call(CMD.decode('utf8').encode('cp1252'), stdout=subprocess.PIPE)
	time.sleep(2)
	
	CMD = "netsh interface ipv4 show dnsserver \"%s\"" % IFNAME
	logging.debug(CMD.decode('utf8').encode('cp850'))
	proc = subprocess.Popen(CMD.decode('utf8').encode('cp1252'), stdout=subprocess.PIPE)
	RES, ERR = proc.communicate()
	logging.debug(RES)
	dnsaddresses = re.findall('(?:[0-9]{1,3}\.){3}[0-9]{1,3}', RES)
	logging.info("DNS server(s) found: %s." % ", ".join(dnsaddresses))
	
	logging.info("Set interface \"%s\" DNS source as localhost."  % IFNAME.decode('utf8').encode('850'))
	CMD = "netsh int ipv4 add dnsserver name=\"%s\" 127.0.0.1 index=1" % (IFNAME)
	logging.debug(CMD.decode('utf8').encode('cp850'))
	subprocess.call(CMD.decode('utf8').encode('cp1252'), stdout=subprocess.PIPE)
	
	return dnsaddresses

def getDNSAdresses(IFNAMES):
	dnsaddresses = set()
	for IF in IFNAMES:
		dnsaddresses.update(set(getDNSfromDHCP(IF)))
	
	return dnsaddresses
	
def getUnboundConfPath():
	unboundservicekey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\services\unbound', 0, _winreg.KEY_WOW64_32KEY | _winreg.KEY_READ | _winreg.KEY_QUERY_VALUE | _winreg.KEY_SET_VALUE) 
	unboundservicecmd, type = _winreg.QueryValueEx(unboundservicekey, 'ImagePath')
	logging.debug(unboundservicecmd)
	
	unboundconfmatch = re.match('^.*unbound\.exe.*-c.*"(.*\.conf)".*$', unboundservicecmd)
	logging.debug(unboundconfmatch.group(1))
	return unboundconfmatch.group(1)

	
def generateUnboundDnsConf(STATICDNS, dnsaddresses):
	unboundconfnewlineslist = ['']
	
	for domain, dns in STATICDNS:
		unboundconfnewlineslist.extend(['forward-zone:', '\tname: "%s"' % domain, '\tforward-addr: "%s"' % dns])
	unboundconfnewlineslist.extend(['', 'forward-zone:', '\tname: "."'])
	
	for dns in dnsaddresses:
		unboundconfnewlineslist.append('\tforward-addr: "%s"' % dns)
	unboundconfnewlineslist.append('')
	
	return "\n".join(unboundconfnewlineslist)

	
def reconfigureUnboundService(unboundconfnewlines):
	unboundconf = open("unboundservice.conf.tmpl").read()
	unboundconf += unboundconfnewlines
	logging.debug(unboundconf)
	open(getUnboundConfPath(), "w").write(unboundconf)
	
	logging.info("Restart Unbound service.")
	win32serviceutil.RestartService('unbound')

	
def proc(IFNAMES, STATICDNS):
	logging.debug(IFNAMES)
	logging.debug(STATICDNS)
	
	dnsaddresses = getDNSAdresses(IFNAMES)
	logging.info("Rewrite Unbound configuration.")
	unboundconfnewlines = generateUnboundDnsConf(STATICDNS, dnsaddresses)
	reconfigureUnboundService(unboundconfnewlines)
	logging.info("Done.")

	
if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Get DNS servers from dhcp, reconfigure local Unbound DNS resolver', epilog="Then restart service")
	parser.add_argument('-i', '--network-interface', dest='nic', default='["Connexion au réseau local", "Connexion réseau sans fil"]', metavar='IFNAME', help='Network interface name')
	parser.add_argument('-d', '--domain-dns', dest='dnslist', default='[]', metavar='DNS_TUPLE_LIST', help='list of additional domains/dns address tuple')
	parser.add_argument("-V", "--verbose", action="store_true", dest="verbose", default=False, help="enable verbose mode")
	args = parser.parse_args()
	
	if args.verbose:
		logging.basicConfig(level=logging.DEBUG, format='%(message)s')
	else:
		logging.basicConfig(level=logging.INFO, format='%(message)s')
	
	proc(ast.literal_eval(args.nic), ast.literal_eval(args.dnslist))
	