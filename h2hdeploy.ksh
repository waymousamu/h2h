#!/bin/ksh
# deployH2H.ksh - perform H2H deployment
# 
# Author : Mahesh Devendran, WebSphere Support, PIU Team
# 
# copyright (c) 2009, Euroclear
#
java -Dpython.path=lib -jar lib/jython.jar scripts/H2HDeployEngine.py $*
