#! /bin/python

import argparse
import _winreg
import socket
import sys
import win32serviceutil


if __name__=='__main__':
	parser = argparse.ArgumentParser(description='Switch synergy server address in Windows registry', epilog="Then restart service")
	parser.add_argument('host', metavar='HOST', help='New synergy server IP address')
	args = parser.parse_args()
		
	try:
		socket.inet_aton(args.host)
	except socket.error:
		sys.stderr.write('%s is not a valid host\n' % args.host)
		sys.exit(-1)
	
	hostregkey = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\Synergy\\Synergy', 0, _winreg.KEY_READ | _winreg.KEY_QUERY_VALUE | _winreg.KEY_SET_VALUE) 
	oldhost, type = _winreg.QueryValueEx(hostregkey, 'serverHostname')
	print 'Change synergy server from %s to %s' % (oldhost, args.host )
	_winreg.SetValueEx(hostregkey, 'serverHostname', 0, type, args.host)
	_winreg.FlushKey(hostregkey)

	cmdregkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Synergy', 0, _winreg.KEY_WOW64_64KEY | _winreg.KEY_READ | _winreg.KEY_QUERY_VALUE | _winreg.KEY_SET_VALUE) 
	oldcmd, type = _winreg.QueryValueEx(cmdregkey, 'Command')
	_winreg.SetValueEx(cmdregkey, 'Command', 0, type, oldcmd.replace(oldhost, args.host))
	_winreg.FlushKey(cmdregkey)
	
	win32serviceutil.RestartService('Synergy')


	
	
