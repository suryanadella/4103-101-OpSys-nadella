#!/usr/bin/python
import sys
import driver
import os
import thread

# Class for command
class Cmd():
    def __init__(self,cmd,inp=None,out=None,append=False):
        c = cmd.split()
        self.params = []
        # Split command and argv
        if len(c) ==0:
            self.cmd = ""
        elif len(c)==1:
            self.cmd = c[0]
        else:
            self.cmd = c[0]
            self.params = c[1:]

        # Set input output
        self.inp = inp
        self.out = out
        self.append = append
        self.inptext = None

    # Function to execute command
    def execute(self,prev=None):
        cmdlist = ['ls','mkdir','cd','pwd','cp','mv','rm','rmdir','cat',
                   'less','head','tail','grep','wc','sort','who','chmod']

        if self.cmd=="":
            return False

        # Check if command is in list
        if self.cmd in cmdlist:
            
            # Pipe  previous output
            if type(prev) is list:
                self.inptext = prev

            if self.inp !=None:
                self.load_input()

            # Execute command
            func = getattr(driver,self.cmd,None)
            flag = func(self.params,self.inptext)

            # Dump if needed
            if self.out !=None:
                if self.append==True:
                    fout = open(self.out,'a')
                else:
                    fout = open(self.out,'w')
                
                # Write to file
                if type(flag) is list:
                    for line in flag:
                        fout.write(line)
                fout.close()

                return True

            if flag!=False:
                return flag
        else:
            print "Command not found:", self.cmd

    # Function to load input file
    def load_input(self):
        if not os.path.exists(self.inp):
            print "shell: %s does not exist" % self.inp
            return

        self.inptext = [l for l in open(self.inp)]

# Function to parse command line
def parse(shell):

    cmds = [c.strip() for c in shell.split('|')]
    c = extract(cmds[0])

    if c==False:
        return False

    prev = c.execute()
    for cmd in cmds[1:]:
        if prev == False:
            return False
        c = extract(cmd)
        prev = c.execute(prev=prev)

    if type(prev) is list:
        for line in prev:
            print line.strip()

    return True

# Function to extract command name
def extract(cmd):
    x1 = cmd.find(' > ')
    n1 = cmd.count(' > ')

    x2 = cmd.find(' < ')
    n2 = cmd.count(' < ')

    x3 = cmd.find(' >> ')
    n3 = cmd.count(' >> ')


    if n1==0 and n2==0 and n3==0:
        # Single command
        c = Cmd(cmd)
    elif n1==1 and n2==0 and n3==0:
        # Write output
        x = cmd.split(' > ')
        c = Cmd(x[0],out=x[1])
    elif n1==0 and n2==1 and n3==0:
        # Get input
        x = cmd.split(' < ')
        c = Cmd(x[0],inp=x[1])
    elif n1==0 and n2==0 and n3==1:
        # Append output
        x = cmd.split(' >> ')
        c = Cmd(x[0],out=x[1],append=True)
    elif n1==1 and n2==1 and n3==0:
        # Get input,write output
        if x1>x2:
            x = cmd.split(" < ")
            y = x[1].split(" > ")
            c = Cmd(x[0],inp=y[0],out=y[1])
        else:
            print "Invalid syntax"
            return False
    elif n1==0 and n2==1 and n3==1:
        # Get input,append output
        if x3>x2:
            x = cmd.split(" < ")
            y = x[1].split(" >> ")
            c = Cmd(x[0],inp=y[0],out=y[1],append=True)
        else:
            print "Invalid syntax"
            return False
    else:
        print "Invalid syntax"
        return False
        
    return c

