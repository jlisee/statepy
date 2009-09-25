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
# File:  statepy/task.py

# STD Imports

# Project Imports
import ext.core as core
import ram.ai.state as state

# Special event that denotes 
TIMEOUT = core.declareEventType('TIMEOUT')        

class Next(state.State):
    """
    Special state denotes that the next task should be moved to
    """
    pass

class Failure(state.State):
    """
    Special state denotes that the task failed in an *unrecoverable* way.
    """
    pass

class End(state.State):
    """
    Special state that denotes the complete end of the state machine
    """
    pass

class Task(state.State):
    """
    Encapsulates a single AI task, like completing an objective.  It allows for
    the implementation and testing of such tasks without concern for what comes
    before, or after said task.
    
    It queries the AI subsystem to ask which state is after itself, and 
    replaces the marker ram.ai.task.Next state with that state. It also also
    handles all the timeout machinery internally.
    """
    def __init__(self, config = None, **subsystems):
        # Call the super class
        state.State.__init__(self, config, **subsystems)
        
        # Dynamically create our event
        self._timeoutEvent = core.declareEventType(
            'TIMEOUT_' + self.__class__.__name__)
        
        # From the AI grab our next task
        self._nextState = self.ai.getNextTask(type(self))
        self._failureState = self.ai.getFailureState(type(self))
    
        # Timeout related values, set later on
        self._hasTimeout = False
        self._timeoutDuration = None
        self._timer = None
    
    @property
    def timeoutEvent(self):
        return self._timeoutEvent
    
    @property
    def timeoutDuration(self):
        return self._timeoutDuration
        
    def transitions(self):
        """
        A dynamic transition function which allows you to wire together a 
        missions dynamically.
        """
        baseTrans = self._transitions()
        newTrans = {}
        for eventType, nextState in baseTrans.iteritems():
            # Catch the timeout event and replace with our class specific 
            # timeout event type
            if eventType == TIMEOUT:
                eventType = self._timeoutEvent
                self._hasTimeout = True
                
            
            if nextState == Next:
                # If the next state is the special Next marker state, swap it 
                # out for the real next state
                nextState = self._nextState
            elif nextState == Failure:
                # If that state is the special failure marker state, swap it 
                # out for the real failure state
                if self._failureState is None:
                    raise "ERROR: transition to non existent failure state"
                nextState = self._failureState
            
            # Store the event
            newTrans[eventType] = nextState
            
        return newTrans

    @staticmethod
    def getattr():
        return set(['timeout'])
    
    def enter(self, defaultTimeout = None):
        if self._hasTimeout:
            # Get timeout duration from configuration file
            if defaultTimeout is None:
                self._timeoutDuration = self._config['timeout']
            else:
                self._timeoutDuration = self._config.get('timeout', 
                                                          defaultTimeout)
            # Start our actual timeout timer
            self._timer = self.timerManager.newTimer(self._timeoutEvent, 
                                                    self._timeoutDuration)
            self._timer.start()
            
    def exit(self):
        if self._timer is not None:
            self._timer.stop()
