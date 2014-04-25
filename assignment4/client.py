from network import Handler, poll
import sys
from threading import Thread
from time import sleep
import msvcrt


myname = raw_input('What is your name? ')

class Client(Handler):
    
    def on_close(self):
    	global running
    	global sys
        self.do_send({'user': myname, 'txt': 'quit'})
        print "**** Disconnected From Server ****"
        running = 0
        raise SystemExit

    
    def on_msg(self, msg):
    	if msg != "close":
        	print msg
        else:
        	self.do_close()
        	
        
host, port = 'localhost', 8888
client = Client(host, port)
client.do_send({'join': myname})
running = 1

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds
                            
thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies 
thread.start()

while running:
	
	mytxt = sys.stdin.readline()
	if mytxt == "quit":
		client.on_close()
	else:
		client.do_send({'speak': myname, 'txt': mytxt})