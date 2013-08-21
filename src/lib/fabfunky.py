#!/usr/bin/env python

# Fabric python magic with the fabfunky functions for cloudPwn

from src.core.config import get_config
from fabric.api import *
from fabric.colors import green, yellow, red
from fabric.state import connections
from time import sleep

__author__ = 'David Bressler (@bostonlink), GuidePoint Security LLC'
__copyright__ = 'Copyright 2013, GuidePoint Security LLC'
__credits__ = ['GuidePoint Security LLC']
__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'David Bressler (@bostonlink), GuidePoint Security LLC'
__email__ = 'david.bressler@guidepointsecurity.com'
__status__ = 'Development'

# Parsing the config file
config = get_config()

def conn_est(host, user, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey), hide("running"):
			print green(run("echo 'Connection Established to %s'" % host))

def move(host, user, source, dest, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey), hide("running"):
		sudo("mv %s %s" % (source, dest))

def apache_start(host, user, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey), hide("running"):
		return sudo("service apache2 start")

def apache_stop(host, user, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey), hide("running"):
		return sudo("service apache2 stop")

def apache_restart(host, user, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey), hide("running"):
		return sudo("service apache2 restart")

def file_upload(host, user, lfile, rfile, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey, warn_only = True):
		return put(lfile, rfile)

def set_auto(host, user, autofile, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey, warn_only = True):
		uploaddir = "/tmp/autoset.txt"
		file_upload(host, user, autofile, uploaddir, sshkey)
		file_upload(host, user, "config/autoset/autoset.sh", "/tmp/", sshkey)
		screen = run("bash /tmp/autoset.sh")
		sleep(1)
		run("rm -f /tmp/autoset.sh")
		run("rm -f /tmp/autoset.txt")
		return screen

def nmap_syn(host, user, iplist, opts, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey, warn_only = True):
		f = open('data/temp/nmap.sh', 'w')
		f.write("mkdir nmap\n")
		f.write("cd nmap\n")
		f.write("sudo screen -A -m -d -L -S NMAP nmap -sS %s %s\n" % (iplist, opts))
		f.write("sudo screen -ls\n")
		f.close()
		file_upload(host, user, 'data/temp/nmap.sh', '/tmp/nmap.sh', sshkey)
		screen = run("bash /tmp/nmap.sh")
		local("rm -f data/temp/nmap.sh")
		return screen

def interactive_shell(host, user, cmd, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey, warn_only = True):
		try:
			open_shell(command=cmd)

		except KeyboardInterrupt:
			print yellow("Exiting shell...")

def clean_local():
	with hide("running"):
		local("rm -f data/temp/*")
		print yellow("Local temporary files cleaned up... Done!")

def disconnect_all():
	for key in connections:
		print yellow("\nDisconnecting from %s" % key)
		connections[key].close()
    	del connections[key]

# TODO grab metasploit and meterpreter logs within this function
def get_logz(host, user, sshkey):
	with settings(host_string = host, user = user, key_filename = sshkey, warn_only =  True):
		print green("Pulling remote logs from instance.....")
		get("/usr/share/set/screenlog.0", "data/remote_logs/")
		get("~/.set/reports/*", "data/remote_logs")
		print green("Remote logs sucessfully saved to the data directory...")