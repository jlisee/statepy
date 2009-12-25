#!/usr/bin/env python

# Copyright (c) 2009, Joseph Lisee
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of StatePy nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Joseph Lisee ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <copyright holder> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Joseph Lisee
# File: test_docs.py

"""
Makes sure all given docs examples produce the expected outputs.
"""

# Python Imports
import os
import sys
import difflib
import subprocess

def main(argv = None):
    if argv is None:
         argv = sys.argv

    # Get the directory all the docs are in
    docDir = sys.path[0]

    # Get the list of all docs files and the output files
    files = os.listdir(docDir)
    docNames = [d[:-3] for d in files if d.endswith('.py')]
    docNames.remove('test_docs')
    outputNames = [o[:-4] for o in files if o.endswith('.out')]

    # Find docs with no output and output with no docs to report to the user
    docs = set(docNames)
    output = set(outputNames)
    noDocs = output - docs
    noOutput = docs - output

    if len(noDocs):
        docStr = ', '.join(noDocs)
        print 'WARNING: The following files have no docs: %s' % docStr

    if len(noOutput):
        outputStr = ', '.join(noOutput)
        print 'WARNING: The following files have no output: %s' % outputStr

    # Find the docs that have matched output and run them and collect output
    usableDocs = docs & output

    # Create environment that puts our library on the python path
    runEnv = {'PYTHONPATH' : os.path.join(docDir, '..')}

    # Check each doc
    for doc in usableDocs:
        # Build the absolute path to the file
        docFile = doc + '.py'
        docPath = os.path.join(docDir, docFile)

        # Create a popen object which sends stderr and stdout to memory
        proc = subprocess.Popen(['python', docPath], env = runEnv,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.STDOUT)

        # Run it to completion and get the return code
        ret = proc.wait()

        gottenLines = []
        if ret is 0:
            gottenLines = proc.stdout.readlines()
        else:
            print 'ERROR: %s returned with: %d' % (docFile, ret)
            
        # Get the expected output
        outFile = doc + '.out'
        output = open(os.path.join(docDir, outFile))
        expectedLines = output.readlines()

        # Compare the results
        diff = difflib.unified_diff(expectedLines, gottenLines,
                                    fromfile = outFile,
                                    tofile = '<%s output>' % docFile)
        diffStr = ''.join(diff)

        if len(diffStr):
            print 'ERROR: doc file "%s"differs from expected output' % docFile
            print diffStr

if __name__=='__main__':
   sys.exit(main())
