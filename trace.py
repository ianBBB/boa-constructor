#-----------------------------------------------------------------------------
# Name:        trace.py
# Purpose:     
#
# Author:      Ian Baker
#
# Created:     2023/03/25
# RCS-ID:      $Id: module1.py $
# Copyright:   (c) 2023
# Licence:     none
#-----------------------------------------------------------------------------
# Purpose: This module defines a static  variable for controlling
# the trace function
trace_is_on = False

#---------------------------------------------------------
#
# Instructions
#
# Typically, you are interested in what is happening inside a particular section of code.
# To do that , you need to set it up.
#
# First, place this line with the other import statements near the top of the module of interest.
#
#       import trace
#
# Place this line at the beginning of the code section of interest;
#
#       trace.trace_is_on=True
#
# At the end of the code, place this line;
#
#       trace.trace_is_on=False
#
# For Boa to produce a trace, you need to start it with a "-T" switch. Open a terminal, change directory
# to the location/directory Boa resides in and use this command;
#
#       python Boa.py -T
#
# You will find the trace in a file called "Boa.trace" in the same directory as Boa.
#
# When you are finished, don't forget to remove the import statement and the trace_is_on assignments.
#
# Good Luck!
#
#----------------------------------------------------------





