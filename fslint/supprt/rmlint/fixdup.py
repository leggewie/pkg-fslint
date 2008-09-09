#!/usr/bin/env python
# This is called by findup automatically don't call explicitly
# unless you really know what you're doing.
#
# It expects lines in the format:
# filename1
# filename2
#
# filename3
# filename4
# ...

import sys, string, os, tempfile

link=1
dryRun=0
if len(sys.argv) == 2:
    if sys.argv[1] == "del":
        link=0
    elif sys.argv[1] == "tdel":
        link=0
        dryRun=1
    elif sys.argv[1] == "tmerge":
        dryRun=1

ingroup = 0
for line in sys.stdin.xreadlines():
    line = string.strip(line)
    if line == '':
        ingroup = 0
    else:
        if not ingroup:
            keepfile = line
            ingroup = 1
            if dryRun:
                print "\n\nkeeping:    ", keepfile + "\n",
                if link:
                    print "hardlinking:",
                else:
                    print "deleting:",
        else:
            if dryRun:
                print line,
            else:
                dupfile = line
                dupdir = os.path.dirname(dupfile)
                tmpfile = tempfile.mktemp(dir=dupdir)
                try:
                    if link:
                        try:
                            os.link(keepfile,tmpfile)
                        except OSError, value:
                            if value.errno == 18: #EXDEV
                                os.symlink(os.path.realpath(keepfile),tmpfile)
                            else:
                                raise
                        os.rename(tmpfile, dupfile)
                    else:
                        os.unlink(dupfile)
                except OSError:
                    sys.stderr.write(str(sys.exc_value)+'\n')
                try:
                    #always try this as POSIX has bad requirement that
                    #rename(file1,file2) where both are links to the same
                    #file, does nothing, and returns success. So if user
                    #merges files multiple times, tmp files will be left.
                    os.unlink(tmpfile)
                except:
                    pass
