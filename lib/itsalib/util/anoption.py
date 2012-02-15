# Copyright (C) 2007 Laurent A.V. Szyster
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License as
# published by the Free Software Foundation.
#
#    http://www.gnu.org/copyleft/gpl.html
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"http://laurentszyster.be/blog/anoption/"

import sys, re, inspect

options = re.compile ('^--?([0-9A-Za-z_]+?)(?:=(.+)?)?$')

def doc (fun):
        named, collection, extension, defaults = inspect.getargspec (fun)
        O = len (defaults or ())
        M = len (named) - O
        mandatory = ", ".join (named[:M])
        if O > 0:
                optionals = ', '.join ((
                        '-%s=%r' % (named[M+i], defaults[i]) 
                        for i in range (O)
                        ))
                if extension:
                        optionals += ', ...'
                if collection:
                        if M > 0:
                                return '%s {%s} [...]' % (
                                        mandatory, optionals
                                        )
                
                        return '{%s} [...]' % optionals

                if M > 0:
                        return '%s {%s}' % (mandatory, optionals)
        
                return '{%s}' % optionals
        
        if collection:
                if M > 0:
                        return '%s [...] ' % mandatory
                
                return '[...]'

        return mandatory


def cast (value, default):
        t = type (default)
        if t == bool:
                return (value != 'no' and bool (value))

        return t (value)
                
def cli (fun, argv=sys.argv[1:], err=(
        lambda msg: sys.stderr.write (msg+'\r\n') or False
        )):
        named, collection, extension, defaults = inspect.getargspec (fun)
        N = len (named)
        O = len (defaults or ())
        M = N - O
        mandatory = set (named[:M])
        names = set ()
        args = []
        kwargs = {}
        ordered = 0
        for value in argv:
                m = options.match (value)
                if m:
                        name, option = m.groups ()
                        if name in named:
                                order = named.index (name)
                                try:
                                        kwargs[name] = cast (
                                                option, defaults[-(N-order)]
                                                )
                                except:
                                        return err ('illegal option ' + name)
                                
                        elif extension:
                                kwargs[name] = option
                elif ordered < N:
                        name = named[ordered]
                        names.add (name)
                        if ordered > M:
                                try:
                                        value = cast (
                                                value, defaults[ordered-M]
                                                )
                                except:
                                        return err (
                                                'illegal argument ' + name
                                                )
                                                
                        args.append (value) 
                        ordered += 1
                elif collection:
                        args.append (value)
                else:
                        return err ('too many arguments')
                        
        if len (args) < M:
                return err ('too few arguments')
                
        for i in range (1, N - ordered + 1):
                kwargs.setdefault(named[-i], defaults[-i])
                
        names.update (kwargs.keys ())
        if not mandatory.issubset (names):
                return err ('missing argument(s): ' + ', '.join (
                        mandatory.difference (names)
                        ))
        
        return fun (*args, **kwargs)