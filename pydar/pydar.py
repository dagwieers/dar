
# from datetime import date

# set of shell options not implemented
# set -p #-u -f

import time, sys, re

class log:
    def __init__(self):
        self.errorlog = ""
        # debug = 1
        # info = 2
        # warn = 3
        # error = 4
        self.loglevel = 1
        # boolean: error occurred?
        self.errorseen = 0
    
    def timestamp(self):
		# in shell: echo $(date +'%h %d %H:%M:%S')
		return time.strftime("%h %d %H:%M:%S")

    def debug(self, logstring):
        if self.loglevel <= 1:
            self.logscreen("DEBUG: " + logstring)
        self.logbuffer("DEBUG: " + logstring) 
    
    def info(self, logstring):
        if self.loglevel <= 2:
            self.logscreen("INFO: " + logstring)
        self.logbuffer("INFO: " + logstring) 
    
    def warn(self, logstring):
        if self.loglevel <= 3:
            self.logscreen("WARN: " + logstring)
        self.logbuffer("WARN: " + logstring) 
    
    def error(self, logstring):
        self.errorseen = 1
        if self.loglevel <= 4:
            self.logscreen("ERROR: " + logstring)
        self.logbuffer("ERROR: " + logstring) 
    
    def logscreen(self, logstring):
        msg = self.timestamp() + " " + logstring + "\n"
        sys.stderr.write(msg)
        
    def logbuffer(self, logstring):
        msg = self.timestamp() + " " + logstring
        self.errorlog = self.errorlog + logstring + "\n"

    def die(self, logstring):
        if self.errorseen:
			self.logscreen(logstring + " exiting")
			sys.exit(1)
        else:
			self.logscreen("exciting succesfully")
			sys.exit(0)
 


class functions:
	def __init__(self):
		self.darconfig = "/etc/dar/pydar.conf"
		
	def clean_env(self):
		print "clean_env not implemented!"

	
	def rpmconf(configVal):
		self.config = configVal
		if self.specfile == "":
			return 1


class specfile:
    def __init__(self, specfile, mylog):
        self.specfile = specfile
        self.log = mylog
        self.values = {}
        self.parseFile()
        
    def parseFile(self):
        f = open(self.specfile, 'r')
        line = f.readline()
        regex = re.compile('^([a-zA-Z0-9]*) *: *(.*)$');
        self.fullcontents = '';
        while line != '':
            self.fullcontents = self.fullcontents + line
            l = line.strip()
            result = regex.match(l)
            if result:
                name = result.group(1)
                value = result.group(2)
                self.log.debug("name is " + name + " and value is " + value)
                self.values[name] = value
            line = f.readline()
        
class config:
    def __init__(self):
        self.root = "/mnt/dar"
        self.dists = []        
        