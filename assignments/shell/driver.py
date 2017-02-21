#!/usr/bin/python

import sys
import os
import pwd as ppwd
import grp,stat
import time
import shutil
import psutil

# Function to convert mode numbers to character
# Called by: ls
def get_mode_info(mode):
    perms = "-"

    if stat.S_ISDIR(mode):
        perms = "d"
    elif stat.S_ISLNK(mode):
        perms = "l"
    mode = stat.S_IMODE(mode)
    for who in "USR", "GRP", "OTH":
        for what in "R", "W", "X":
            # Lookup attribute at runtime using getattr
            if mode & getattr(stat,"S_I"+what+who):
                perms = perms+what.lower()
            else:
                perms = perms+"-"
    return (perms)

# Function to convert filesize into human-readable
# Called by: ls
def human_size(size):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(size) < 1024.:
            return "%3.1f%s" % (size, unit)
        size /= 1024.
    return "%.1f%s" % (size, 'Y')


# ls    : list files and dir
def ls(argv,inp):

    # Parse argv
    if argv:
        params = argv[0]
        if params[0]!='-':
            print "ls: Invalid option"
            return False
    else:
        params = []

    files = os.listdir(".")

    # Hide hidden file
    if 'a' not in params:
        files = [f for f in files if f[0]!='.']

    # Sort files
    files = sorted(files)

    if 'l' in params:
        rlist = []
        for f in files:
            stat_info = os.lstat(f)
            
            mode = get_mode_info(stat_info.st_mode)     # Get file mode
            name = ppwd.getpwuid(stat_info.st_uid)[0]   # Get file username
            group = grp.getgrgid(stat_info.st_gid)[0]   # Get file group

            nlink = stat_info.st_nlink                  # Get no of link

            #Get time stamp of file
            ts = stat_info.st_mtime
            time_fmt = "%b-%e-%Y"
            time_str = time.strftime(time_fmt, time.gmtime(ts))

            # Get filesize
            size = stat_info.st_size
            if 'h' in params:
                size = human_size(size)
            s = "%s %s %s %s %s %s %s\n" % (mode,nlink,name,group,size,time_str,f)
            rlist.append(s)
        return rlist

    else:
        return [" ".join(files)+"\n"]
    return


# mkdir : make dir
def mkdir(argv,inp):

    # Parse argv
    if argv:
        directory = argv[0]
    else:
        print "mkdir: missing operand"
        return False

    # Create directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print "mkdir: cannot create directory '%s': File exists" % directory
        return False

    return True


# cd    : change dir
def cd(argv,inp):
    # Parse argv
    if argv:
        directory = argv[0]
    else:
        directory = None

    # Go to home directory
    if directory==None or directory=="~":
        os.chdir(os.path.expanduser("~"))
    else:
        if os.path.exists(directory):
            os.chdir(directory)
        else:
            print "shell: cd: %s: No such file or directory" % directory
            return False

    return True


# pwd   : display current dir
def pwd(argv,inp):
    return [os.getcwd()+"\n"]


# cp    : copy file
def cp(argv,inp):
    # Parse argv
    if len(argv)==2:
        file1 = argv[0]
        file2 = argv[1]
    else:
        print "cp: missing operand"
        return False

    # Check if file1 exist
    if not os.path.exists(file1):
        print "cp: '%s': No such file or directory" % file1
        return False

    # Check if file1 is a directory
    if os.path.isdir(file1):
        print "cp: omitting directory '%s'" % file1
        return False
    # Check if file1 and file2 are same
    if file1 == file2:
        print "cp: '%s' and '%s' are the same file" % (file1,file2)
        return False

    # Copy file
    shutil.copy2(file1,file2)   
    return True


# mv    : move file
def mv(argv,inp):
    # Parse argv
    if len(argv)==2:
        file1 = argv[0]
        file2 = argv[1]
    else:
        print "mv: missing operand"
        return False

    # Move file
    if not os.path.exists(file1):
        print "mv: '%s': No such file or directory" % file1
        return False

    shutil.move(file1,file2)

    return True


# rm    : remove file
def rm(argv,inp):
    # Parse argv
    if argv:
        filename = argv[0]
    else:
        print "rm: missing operand"
        return False

    # Check if file exist
    if not os.path.exists(filename):
        print "rm: cannot remove '%s': No such file or directory" % filename
        return False

    # Check if file is a directory
    if os.path.isdir(filename):
        print "rm: cannot remove '%s': Is a directory" % filename
        return False

    # Remove file
    os.remove(filename)

    return True


# rmdir : remove dir
def rmdir(argv,inp):
    # Parse argv
    if argv:
        directory = argv[0]
    else:
        print "rmdir: missing operand"
        return False

    # Check if directory exist
    if not os.path.exists(directory):
        print "rmdir: failed to remove '%s': No such file or directory" % directory
        return False

    # Check if file is a directory
    if not os.path.isdir(directory):
        print "rmdir: failed to remove '%s': Not a directory" % directory
        return False

    # Remove directory (even if it's not empty, because screw it)
    shutil.rmtree(directory)

    return True


# cat   : display file
def cat(argv,inp):
    # Parse argv
    if argv:
        filename = argv[0]
        
        # Check if file exist
        if not os.path.exists(filename):
            print "cat: %s: No such file or directory" % filename
            return False

        return [l for l in open(filename,'r')]

    elif inp!=None:
        for line in inp:
            print line.strip()
    else:
        print "cat: missing operand"
        return False


# less  : display a file a page at a time
# TODO: do this
def less(argv,inp):
    if argv:
        filename = argv[0]
        # Check if exist
        if not os.path.exists(filename):
            print "less: %s: No such file or directory" % filename
            return False

        # Read input file
        inputs = [l for l in open(filename,'r')]

    elif inp!=None:
        inputs = inp
    else:
        print "less: missing operand"
        return False

    for l,line in enumerate(inputs):
        print line.strip()
        if l>0 and l % 20 == 0:
            raw_input("Press enter to continue..")

    return True

# head  : display the first few lines of file
def head(argv,inp):
    if argv:
        # Read from file
        filename = argv[0]
        if not os.path.exists(filename):
            print "head: %s: No such file or directory" % filename
            return False

        # Open input file
        fin = open(filename,'r')
        rlist = []
        for i in range(10):
            line = fin.readline()
            if not line:
                break
            rlist.append(line)
        fin.close()
        return rlist        

    elif inp != None:
        return inp[:10]

    else:
        print "head: missing operand"
        return False


# tail  : display the last few lines of file
def tail(argv,inp):
    if argv:
        # Read from file
        filename = argv[0]

        if not os.path.exists(filename):
            print "tail: %s: No such file or directory" % filename
            return False

        # Read input file
        inputs = [l for l in open(filename,'r')]
        inputs = inputs[-10:]
        return inputs

    elif inp!=None:
        # Print from input
        return inp[-10:]
    else:
        print "tail: missing operand"
        return False
        
    return True


# grep  : search a file for keywords
def grep(argv,inp):
    if len(argv)==2:
        keyword = argv[0]
        filename = argv[1]

        # Read input file
        if not os.path.exists(filename):
            print "grep: %s: No such file or directory" % filename
            return False

        # Read input file
        inputs = [l for l in open(filename,'r')]

    elif len(argv)==1 and inp!=None:
        keyword = argv[0]
        inputs  = inp 
    else:
        print "grep: missing operand"
        return False

    # Parse keyword   
    if keyword[0] == "'" and keyword[-1]=="'":
        keyword = keyword[1:-1]
    else:
        print "USAGE: grep 'keyword' file"
        return False

    return [l for l in inputs if keyword in l]


# wc    : count number of lines/words/char
def wc(argv,inp):

    if argv:
        filename = argv[0]

        # Check if exist
        if not os.path.exists(filename):
            print "wc: %s: No such file or directory" % filename
            return False

        # Check if file is a directory
        if os.path.isdir(filename):
            print "wc: %s: Is a directory" % filename
            return False

        # Read input file
        inputs = [l for l in open(filename,'r')]

    elif inp!=None:
        inputs = inp
    else:
        print "wc: missing operand"
        return False
    
    # Word and character count
    w = 0
    c = 0
    l = len(inputs)
    for line in inputs:
        c = c + len(line)
        w = w + len(line.split())
    if inp==None:
        s = "%s %s %s %s\n" % (l,w,c,filename)
    else:
        s = "%s %s %s\n" % (l,w,c)
    return [s]


# sort: sort data
def sort(argv,inp):
    if argv:
        filename = argv[0]
        # Check if exist
        if not os.path.exists(filename):
            print "sort: %s: No such file or directory" % filename
            return False

        # Read input file
        inputs = [l for l in open(filename,'r')]

    elif inp!=None:
        inputs = inp
    else:
        print "sort: missing operand"
        return False

    # Sort inputs
    inputs = sorted(inputs)
    return inputs


# who: list logged in users
def who(argv,inp):
    users = os.path.expanduser('~').split('\\')[-1]
    vlist = []
    vlist.append(users)
    return vlist


# chmod: change permission
def chmod(argv,inp):
    if len(argv)==2:
        mode = int(argv[0],8)
        filename = argv[1]

        # Check if exist
        if not os.path.exists(filename):
            print "chmod: %s: No such file or directory" % filename
            return False
        
        # Set chmod
        os.chmod(filename,mode)

    else:
        print "chmod: missing operand"
        return False
        
    return True
