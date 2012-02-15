'''
====================================================
 `doctest1`
====================================================

General tests showing basic usage.

.. sourcecode:: python

    >>> from itsalib import *

First remember our current directory:

.. sourcecode:: python

    >>> CWD = cwd()

and disable the step number in log output:

.. sourcecode:: python

    >>> log.disable_step()

Test string:

.. sourcecode:: python

    >>> TESTSTRING1 = """TEST
    ... TEST
    ... TEST
    ... random text ${fee} here
    ... TEST
    ... ${fi}
    ... TEST"""

Create a temporary working directory:

.. sourcecode:: python

    >>> working = mktempdir()
    INFO    Creating temporary directory.
    INFO    Temporary directory is: ...

Change directory to the temporary directory just created, and
create a project sub-directory structure within it.

.. sourcecode:: python

    >>> chdir(working)
    INFO    Changing directory to ...
    >>> project = 'testing'
    >>> mkdir(project)
    INFO    Creating directory: ...
    >>> chdir(project)
    INFO    Changing directory to ...
    >>> mkdir('a/b')
    INFO    Creating directory: ...
    INFO    Creating directory: ...
    >>> mkdir('c/d/e')
    INFO    Creating directory: ...
    INFO    Creating directory: ...
    INFO    Creating directory: ...

Create a dummy file and copy it to an existing directory: 

.. sourcecode:: python

    >>> f = mktempfile(working)
    INFO    Creating temporary file in directory: ...
    INFO    Temporary file is: ...
    >>> tmpfilename = f.name
    >>> f.write(TESTSTRING1)
    >>> f.close()

Copy dummy file to an existing directory: 

.. sourcecode:: python

    >>> exists('a/b')
    True
    >>> dst = join('a/b', basename(tmpfilename))
    >>> exists(dst)
    False
    >>> copy(tmpfilename, 'a/b')
    INFO    Copying file: ...
    >>> exists(dst)
    True

Copy the dummy file to a non-existent directory. Destination directories are created as required.

.. sourcecode:: python

    >>> exists('x/y')
    False
    >>> dst = abspath(join('x/y', basename(tmpfilename)))
    >>> exists(dst)
    False
    >>> copy(tmpfilename, 'x/y')
    INFO    Copying file: ...
    INFO    Creating directory: ...
    INFO    Creating directory: ...
    >>> exists('x/y')
    True
    >>> exists(dst)
    True

String replacement and writing a string to file.

.. sourcecode:: python

    >>> s = "#subject# had a #adj# #object#."
    >>> d = {"#subject#": "Mary", "#adj#": "little", "#object#": "lamb"}
    >>> s = multireplace(s, d)
    INFO     Replacing '#subject#' with 'Mary'
    INFO     Replacing '#adj#' with 'little'
    INFO     Replacing '#object#' with 'lamb'
    >>> print s
    Mary had a little lamb.
    >>> write_string(s, join('x', 'rhyme.txt'))
    INFO    Opening file for writing: ...
    INFO    Writing string to file: ...

Rewrite files by replacing string patterns:

.. sourcecode:: python

    >>> data = {'fee': 'FEE', 'fi': 'FI'}
    >>> rewrite_file(dst, data)
    INFO    ...
    >>> #check that the file has been changed
    >>> f = open(dst, 'r')
    >>> s = f.read()
    >>> f.close()
    >>> print s
    TEST
    TEST
    TEST
    random text ${FEE} here
    TEST
    ${FI}
    TEST

Now treat the temp file as a template and make substitutions:

.. sourcecode:: python

    >>> data = {'FEE': '1234', 'FI': '9876'}
    >>> rewrite_template(dst, data)
    INFO    Rewriting template: ...
    INFO    Opening file for reading: ...
    INFO    String template substitution.
    INFO    Substituting FI -> 9876
    INFO    Substituting FEE -> 1234
    INFO    Opening file for writing: ...
    INFO    Writing string to file: ...
    >>> f = open(dst, 'r')
    >>> s = f.read()
    >>> f.close()
    >>> print s
    TEST
    TEST
    TEST
    random text 1234 here
    TEST
    9876
    TEST

Create a copy of the project directory tree.

.. sourcecode:: python

    >>> chdir(working)
    INFO    Changing directory to ...
    >>> project_copy = '%s_copy' % project
    >>> exists(project_copy)
    False
    >>> mirrortree(project, project_copy)
    INFO    Recursive copy: ...
    >>> exists(project_copy)
    True
    >>> #Check whether the two directories have the same content
    >>> set(listdirs(project)) == set(listdirs(project_copy))
    True

Create a tar archive from the project directory.

.. sourcecode:: python

    >>> archive = '%s.tar' % project
    >>> exists(archive)
    False
    >>> tardir(project)
    INFO    tardir ...
    >>> exists(archive)
    True

Remove the directory just tarred, and recreate from the archive.

.. sourcecode:: python

    >>> before = listdirs(project)
    >>> removetree(project)
    INFO    Recursive remove directory: ...
    >>> exists(project)
    False
    >>> untar(archive)
    INFO    untar ...
    >>> exists(project)
    True
    >>> after = listdirs(project)
    >>> len(before) > 0
    True
    >>> set(before) == set(after)
    True

Now create a zip archive.

.. sourcecode:: python

    >>> archive = '%s.zip' % project
    >>> exists(archive)
    False
    >>> zipdir(project)
    INFO    zipdir ...
    >>> exists(archive)
    True


Clean up - remove the temporary working directory and everything beneath it.

.. sourcecode:: python

    >>> chdir(CWD) #change back to original directory
    INFO    Changing directory to ...
    >>> exists(working)
    True
    >>> #Don't want all the output from `removetree`, so disable logging
    >>> log.disable()
    >>> removetree(working)
    >>> exists(working)
    False
    >>> #and re-enable logging
    >>> log.enable()

Ali had some problems with multireplace - testing further:

.. sourcecode:: python

    >>> tmpl = 'abcdef abcdef abcdef'
    >>> data = {'cd': 'QQ'}
    >>> s = multireplace(tmpl, data)
    INFO     Replacing 'cd' with 'QQ'
    INFO     Replacing 'cd' with 'QQ'
    INFO     Replacing 'cd' with 'QQ'
    >>> print s
    abQQef abQQef abQQef
    >>> tmpl = 'ab/opt/wily abcdef abcdef'
    >>> data = {'/opt/wily': '/opt/introscope'}
    >>> s = multireplace(tmpl, data)
    INFO     Replacing '/opt/wily' with '/opt/introscope'
    >>> print s
    ab/opt/introscope abcdef abcdef


'''

if __name__ == '__main__':
    import doctest
    options = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    doctest.testmod(optionflags=options)

