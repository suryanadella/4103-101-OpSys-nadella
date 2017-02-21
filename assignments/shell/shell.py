#!/usr/bin/python
import parser
import threading

history = []

class cmdThread(threading.Thread):
    def __init__(self,cmd):
        threading.Thread.__init__(self)
        self.cmd = cmd
    def run(self):
        parser.parse(self.cmd)

while(True):
    cmd = raw_input("$:")   # Get user input
    if cmd=="":
        continue
    # Set mode
    if cmd[-1] == '&':
        bgdMode = True
        cmd = cmd[:-1]
    else:
        bgdMode = False

    if cmd=="exit":         # Exit
        break
    elif cmd=="history":    # History
        for h,hist in enumerate(history):
            print h+1,hist
    elif cmd[0]=='!' and len(cmd)>1:
        c = int(cmd[1:])-1
        if c>=0 and c<len(history):
            t = cmdThread(history[c])
            t.start()
            
            if not bgdMode:
                t.join()
        else:
            print "Event not found"
    else:
        t = cmdThread(cmd)
        t.start()
        
        if not bgdMode:
            t.join()

        history.append(cmd)
