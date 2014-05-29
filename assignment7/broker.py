from network import Listener, Handler, poll


handlers = {}  # map client handler to user name
names = {} # map name to handler
subs = {} # map tag to handlers

def broadcast(msg):
    for h in handlers.keys():
        h.do_send(msg)


class MyHandler(Handler):
    
    def on_open(self):
        handlers[self] = None
        
    def on_close(self):
        name = handlers[self]
        del handlers[self]
        broadcast({'leave': name, 'users': handlers.values()})
        
    def on_msg(self, msg):
        #boolean for whether the message is a public message
        public = True

        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            names[name] = self
            broadcast({'join': name, 'users': handlers.values()})
        elif 'speak' in msg:
            name, txt = msg['speak'], msg['txt']
            wordlist = msg['txt'].split(" ")
            broadcastlist = []
            removelist = []

            for word in wordlist:
                
                #### subscribe ####
                if word[0] == '+':
                    topic = word[1:]
                    if topic in subs:
                        subs[topic].append(name)
                    else: 
                        subs[topic] = []
                        subs[topic].append(name)
                    #adds word to list of words to be removed
                    removelist.append(word)

                ### publish ###
                elif word[0] == "#":
                    public = False
                    topic = word[1:]
                    if topic in subs:
                        subscribers = subs[topic]

                        for subscriber in subscribers:
                            if subscriber not in broadcastlist:
                                broadcastlist.append(subscriber)

                ### unsubscribe ###
                elif word[0] == "-":
                    topic = word[1:]
                    if topic in subs:
                        subscribers = subs[topic]

                        if name in subscribers:
                            subscribers.remove(name)

                    removelist.append(word)

                ### private message ###
                elif word[0] == "@":
                    public = False
                    recipient = word[1:]
                    if recipient in names:
                        if recipient not in broadcastlist:
                            broadcastlist.append(recipient)

            for word in removelist:
                wordlist.remove(word)

            txt = " ".join(wordlist)

            # if string is not empty, send it 
            if txt:
                # if the message is meant to be public send it to everyone
                if public:
                    broadcast({'speak': name, 'txt': txt})
                else:
                    for client in broadcastlist:
                        names[client].do_send({'speak': name, 'txt': txt})


Listener(8888, MyHandler)
while 1:
    poll(0.05)