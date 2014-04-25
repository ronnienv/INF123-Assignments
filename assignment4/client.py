from network import Handler, poll
import sys
from threading import Thread
from time import sleep


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
            exit()
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
    try:
        mytxt = sys.stdin.readline().rstrip()
        if mytxt == "quit":
            client.do_close()

        else:
    		client.do_send({'speak': myname, 'txt': mytxt})

    except KeyboardInterrupt:
        client.do_close()
        exit()