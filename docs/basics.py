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
# File: basics.py

# Python Imports
import sys

# Import state machine package
import statepy.state

class StateA(statepy.state.State):
    """ Every state class inherits from the a 'State' superclass """
    
    # Here we declare "event" types, currently these must be strings. The 
    # value passed to the function is name of the transition that will be 
    # called if the state transitions on that event.
    TO_B = statepy.state.declareEventType('TO_B_handle')
    LOOP = statepy.state.declareEventType('LOOP_handle')
    
    @staticmethod
    def transitions():
        """
        Static transition table, can be analized by tools. All it has to do is
        return a python dict.

        If you wish you can make this a non-static method but you lose the
        ability to do static instrospection of your state machine.
        """
        return {
            StateA.TO_B : StateB, # Moves us to the B state
            StateA.LOOP : StateA  # States in state, calls transition function
            }
        
    def LOOP_handle(self, event):
        print "Loop back, myVar:",self.myVar
        self.myVar += 5
        
    def TO_B_handle(self, event):
        """ Called whenver the state machine tranistions on the 'TO_B' event"""
        print "Transition on event 'TO_B', myVar:",self.myVar
            
    def enter(self):
        """ Called when the state is entered """
        print "entering A"
        
        # Initialize all state specific "state variables" here each time the
        # state is entered its with a new object so all old self variables are
        # gone
        self.myVar = 5
        
    def exit(self):
        print "Leaving A"

        
TO_END = statepy.state.declareEventType('TO_END')
        
class StateB(statepy.state.State):
    TO_A = statepy.state.declareEventType('TO_A_handle')

    @staticmethod
    def transitions():
        return {
            StateB.TO_A : StateA, # Moves us to the A state
            TO_END : StateEnd  # Moves us to the end state
            }
        
    def TO_END(self, event):
        print "going to the 'End' state"
        
    def TO_A_handle(self, event):
        print "going to 'A' state"
    
    def enter(self):
        print "entering B"
        
    def exit(self):
        print "Leaving B"
        
class StateEnd(statepy.state.State):
    """ 
    Note: since state has no transition table its automatically entered and
    *exited* when you transition into it.
    """

    # No transition table for this state
    
    def enter(self):
        print "entering end"
        
    def exit(self):
        print "exiting end"
    
def main(argv = None):
    if argv is None:
         argv = sys.argv
    
    # Using a state method of the machine class we can write out our state
    # machine in dot format in the file called "state_machine.dot". The given
    # state is where it starts walking the state graph.
    myFile = open('state_machine.dot', 'w')
    statepy.state.Machine.writeStateGraph(fileobj = myFile, startState = StateA)
    myFile.close()
    
    # Create our main object
    machine = statepy.state.Machine()
    
    # Start up the machine with our start state, its automatically entered
    machine.start(startState = StateA)
    print "Machine started" # Note this will *come* after "entering A" has
    
    # Now lets process some events
    machine.injectEvent(StateA.LOOP) # Loop back, we're still in A
    machine.injectEvent(StateA.TO_B) # Now we are in B
    machine.injectEvent(StateB.TO_A) # Back to A
    
    # You can grab the current state object as well
    currentState = machine.currentState()
    print type(currentState)
    
    machine.injectEvent(StateA.TO_B) # Back in B again
    machine.injectEvent(TO_END) # Now lets go to the end

    # After the end event current state is "None" because the state was 
    # exited automatically and had no transitions.

if __name__=='__main__':
   sys.exit(main())
