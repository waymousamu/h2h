#!/usr/bin/env python
"""dbutil.py -- Friendly wrappers for DB-API applications.

dbutil is a middle ground between DB-API and object-relational mappers.
DB-API is so low-level it requires 2-3 steps for every query, which clutters
your code.  Object-relational mappers are so clever it's hard to verify they're
doing the right thing.  dbutil is a straightforward wrapper around
DB-API that encapsulate the tedious parts.  There are methods to generate
SQL pythonically, but no "data object model", just a simple transformation of
arguments to SQL clauses.  You have to know what SELECT and WHERE mean, but you
don't have to get all the quoting and commas in the right places.  To verify
what dbutil is doing, turn on logging to see the actual SQL that's being
generated, or read the source to see the transformations.  There's a lot of
nested method calls but each method is pretty easy to understand.

The .select* methods generate a query, execute it, and return the result in a
format that's convenient for you:
  - a list of mutable dictionaries (default) 
  - a sequence of sequences (DB-API standard) 
  - a single dict or sequence 
  - a single value 
  - a list of values for one column 
  - a dict made from a two-column result 
  - a boolean (were any records found?) 
  - an integer (how many records were found?)  

I find the "list of dictionaries" format especially useful.  You can use the
dicts to gather updates and post them back to the database, or as scratch space
to add keys needed by your view (e.g., your display template).  There's a
function only_some_keys to trim down a larger dict to only the items you want
to post back.

The simplest way to use this module is to set the global variable 'db' to a
DBAPI_Wrapper or MySQLdb_Wrapper instance at the start of your application:
    import MySQLdb
    import dbutil
    conn = MySQLdb.connect(db='test')
    dbutil.db = dbutil.MySQLdb_Wrapper(conn)

Then any module can call methods on the access object:
    records = dbutil.db.select('table1', ['first_name', 'last_name'], dict=True)

If your application needs a second connection for a special purpose, it can
instantiate the wrapper directly and use it.

DBAPI_Wrapper tries to be generic, but there are certain things I don't know
how to do without MySQL-isms.  These are mentioned in the method docstrings.
If you're using a different database you may have to tweak the code a bit and
send me a patch.

There is also a Where class to help build a WHERE expression from search form
criteria.

See the class and method docstrings for more detailed usage.  Those starting
with "**" are the most generally useful.  The test suites, test_dbutil.py and
test_dbutil_where.py, also contains (rudimentary) examples.
http://cafepy.com/quixote_extras/rex/tests/test_dbutil.py
http://cafepy.com/quixote_extras/rex/tests/test_dbutil_where.py

The official download location for this module is:
http://cafepy.com/quixote_extras/rex/dbutil.py

Copyright (C) 2005 Mike Orr <mso@oz.net>
Copying and modification is permitted under the MIT licence:
http://www.opensource.org/licenses/mit-license.php

This module has been tested on Python 2.3.4 and 2.4.1 .

CHANGELOG:
Version 1.0, updated 2005-06-22.
Version 1.1, 2005-06-22.
  - Explain in .insert() and .update() docstring that 'set_dict' values
    must be literals rather than SQL expressions.
  - .insert() has new arg 'replace' that does SQL REPLACE.
Version 1.2, 2005-06-28.
  - Eliminate InsufficientRecordsError.  .select_row() and .select_value()
    now have a 'default' argument, which is returned if no rows match.  They
    return None if no default is specified.
  - .select_dict() forbids keyword arg 'dict'.
Version 1.3, 2005-07-27.
  - Add 'literal' arg to .insert(), .update(), and .make_iru_sql().  This is
    for values that are SQL expressions, which the update dict can't handle
    (it would quote the values).
  - Add 'order' arg to .select_row().  This is the easiest way to get the
    minimum or maximum of a column along with other values from that row.  Use
    a multi-level sort if you need multiple mins/maxes.
2005-10-18.
  - Database.in_list() returns a SQL IN expression.
"""
import logging, pprint, re, sys
from cStringIO import StringIO
try:
    set
except NameError:  # Python < 2.4.
    from sets import Set as set

debug = logging.getLogger('sql').debug  # All SQL statements executed.
debugWhere = logging.getLogger('where').debug  # All WHERE expressions built.

COMPARE_OPERATORS = set(['=', '!=', '<', '>', '<=', '>'])

#### CONVENIENCE GLOBAL FOR APPLICATIONS WITH ONLY ONE CONNECTION ####
db = None

#### FUNCTIONS ####
def escape(s, quote=False):
    """This is a simple implementation of MySQLdb.escape_string.  It's 
       needed by like() and Where so they don't have to depend on MySQLdb or
       a wrapper object for that functionality.  Hopefully it will be valid for
       all DB-API libraries.

       @param quote boolean Add single quotes around the whole thing if
           it's not numeric?
    """
    # Python doesn't allow a string literal to end in a backslash, so we
    # have to add an extra space and then remove it.
    s = s.replace(R'\ '[:-1], R'\\ '[:-1])
    s = s.replace(R'"', R'\"')
    s = s.replace(R"'", R"\'")
    if quote and not s.isdigit():
        s = "'%s'" % s
    return s

def like(field, value):
    """Make a "LIKE" WHERE expression that matches a substring."""
    return field + " LIKE '%" + escape(value) + "%'"

def only_some_keys(dic, *keys):
    """Return a copy of the dict with only certain items present.  The source
       may be any mapping; the result is always a Python dictionary.
       @exc KeyError if a key is not in 'dic'.
    """
    ret = {}
    for key in keys:
        ret[key] = dic[key]   # Raises KeyError.
    return ret

#### SIMPLE WRAPPERS ####
class Database:
    """A simple wrapper around DB-API.  You provide the database connection and
       SQL statements, and it encapsulates the tedious parts.

       This class tries to be generic but contains some MySQLdb-isms I don't
       know how to work around.  It can be subclassed to provide additional
       features for certain database types.
    """

    def __init__(self, conn):
        """@param conn a DB-API database connection; e.g., from
           MySQLdb.connect().
        """
        self.conn = conn

    def get_cursor(self):
        """A generic way to get a new or idle cursor.  This method doesn't
           take arguments so it always returns the default cursor type.
           Subclasses can have optional arguments to choose alternate cursors.
        """
        return self.conn.cursor()

    def interpolate(self, sql, args):
        """A MySQLdb-ism.  Normally in DB-API you call
           cursor.execute(sql, args) and let it handle argument quoting.
           However, in order to log the actual SQL we're about to execute,
           we have to do the expansion ourselves.  I don't know how to do that
           outside MySQLdb.
           'args' must be a sequence if the placeholders are %s, or a mapping
           if they are %(key)s.
        """
        if args is None:
            return sql
        return sql % self.conn.literal(args)

    def escape(self, s):
        """A MySQdb-ism.  Transform a value so it can be plugged into a
           SQL statement.  Put '' around any argument that requires quoting,
           and escape backslashes.
        """
        return self.conn.escape_string(s)

    def execute(self, cursor, sql, args):
        """Execute a SQL command or query in the provided cursor.
           This is mainly for internal use, but is also useful when a user
           wants to do multiple cursor operations after the command (.rowcount,
           .description, .fetchall()), call cursor methods not supported by
           dbutil (e.g., .fetchmany()), or use a custom cursor type.
        """
        real_sql = self.interpolate(sql, args)
        debug(real_sql)
        cursor.execute(real_sql)

    def run(self, sql, args=None):
        """Run a SQL command and return the number of affected rows."""
        cursor = self.get_cursor()
        self.execute(cursor, sql, args)
        return cursor.rowcount

    command = run

    def query(self, sql, args=None, dict=False, rowcount=False):
        """Run a SQL query and return the results.  
        
           @param sql string Any SQL command that returns rows, including
               'SELECT', 'SHOW TABLES', 'DESCRIBE <table>', etc.
           @param args tuple or mapping, depending on the placeholder syntax
               used (%s or %(key)s) and what the underlying database module
               supports.
           @param dict boolean If false, return a sequence of sequences
               (DB-API standard).  If true, return a list of mutable dicts.
           @param rowcount boolean If true, return the number of rows in the
               result rather than the result itself.  

           The "list of dicts" feature is one of the most useful parts of
           dbutil.  You can use the dicts to gather updates and post them back
           to the database, or use the dicts as scratch space to add values
           needed by your view (e.g.., your display template).  Since
           most DB-API implementations do not have this feature in the core, we
           do it ourselves here.
        """
        cursor = self.get_cursor()
        self.execute(cursor, sql, args)
        if rowcount:
            return cursor.rowcount
        records = cursor.fetchall()
        if not dict:
            return records
        # Transform the rows into dicts.
        from __builtin__ import dict as Dict
        fieldNames = [x[0] for x in cursor.description]
        ret = [None] * cursor.rowcount
        for i, row in enumerate(records):
            pairs = zip(fieldNames, row)
            dic = Dict(pairs)
            ret[i] = dic
        return ret

    def in_list(field, values):
        """Return a SQL IN expression."""
        choices = ", ".join(["'%s'" % escape(x) for x in values])
        return "%s IN (%s)" % (sql_field, choices)


class MySQLDatabase(Database):
    """A DB-API wrapper with optimizations for MySQL.
    """
    def get_cursor(self, dict=False):
        """MySQLdb can convert results to dicts at "C" speed during
           the fetch, so we take advantage of it.
        """
        if dict:
            from MySQLdb.cursors import DictCursor
            return self.conn.cursor(DictCursor)
        else:
            return self.conn.cursor()

    def query(self, sql, args=None, dict=False, rowcount=False):
        """Override this just to pass the 'dict' arg to .get_cursor()."""
        cursor = self.get_cursor(dict)
        self.execute(cursor, sql, args)
        if rowcount:
            return cursor.rowcount
        else:
            return cursor.fetchall()

class SQLBuilderMixin:
    """This mixin provides methods for generating SQL."""

    def make_sql(self, command="SELECT", table=None, fields=None,
        where=None, group=None, having=None, order=None,
        limit=None, offset=0):
        """Return the SQL statement implied by the arguments.  This is meant
           for statements that return rows: SELECT, SELECT DISTINCT, SHOW, etc.

           @param See .select() for the argument signatures.
           @return string
        """
        sio = StringIO()
        sio.write(command)
        sio.write(' ')
        if fields is not None:
            sio.write(", ".join(fields))
        if table is not None:
            sio.write("\nFROM %s\n" % table)
        if where is not None:
            sio.write("WHERE %s\n" % where)
        if group is not None:
            sio.write("GROUP BY %s\n" % group)
        if having is not None:
            sio.write("HAVING %s\n" % having)
        if order is not None:
            sio.write("ORDER BY %s\n" % order)
        if limit is not None:
            sio.write("LIMIT %d, %d\n" % (offset, limit))
        return sio.getvalue()

    def make_create_sql(self, table, field_pairs, indexes='', extra=''):
        """Return a SQL statement to create the specified table.

           @param See .create() for the argument signatures.
           @return string
        """
        defs = ["%s %s" % x for x in field_pairs]
        defs = ",\n".join(defs)
        return "CREATE TABLE %s (%s %s) %s" % (table, defs, indexes, extra)

    def make_iru_sql(self, command, table, dic, where=None, literal=None):
        """Return an INSERT, REPLACE, or UPDATE SQL statement.  These three
           statements use the "SET field=value" syntax.

           @param command string The SQL command.
           @param table string The table.
           @param dic dict The 'field: value' items to set.
           @param where string A WHERE expression to limit the rows operated on.
           @param literal String of additional 'field=value, field=value'
               items.  The values are normally SQL expressions
               which cannot go in 'dic' or they would be quoted.  There is
               no provision for replaceable parameters in this string.
           @return string

           The generated SQL will have placeholders in the mapping format
           (%(field)s).  This means any placeholders in the 'where' arg must be
           this format too.  Don't pass such extra items in 'dic' here, but do
           include them in 'args' when the resulting statement is executed.
        """
        set_pairs = ["%s = %%(%s)s" % (x, x) for x in dic.iterkeys()]
        if literal:
            set_pairs.append(literal)
        set_clause = ",\n".join(set_pairs)
        sio = StringIO()
        sio.write("%s %s SET \n" % (command, table))
        sio.write(set_clause)
        sio.write(" ")
        if where:
            sio.write("WHERE %s\n" % where)
        return sio.getvalue()

    def select(self, table, fields, where=None, args=None, dict=True,
        limit=None, offset=0, group=None, having=None, order=None,
        distinct=False, command="SELECT", rowcount=False):
        """Do a query and return the results.

           @param table string The table name.  For joins: "table1, table2",
               "table1 LEFT JOIN table2 ON ...".
           @param fields List of field names or field expressions.  Examples:
               "fname", "fname AS first_name", "CURRENT_DATE AS today",
               "2 + 2 AS four", "table1.cust_id AS cust_id",
               "SUM(amount)".  If you use an aggregate expression like SUM,
               you must use the 'group' argument too.
           @param where string The entire WHERE clause.  Examples:
               where="cust_id = %s"
               where="date_due < CURRENT_DATE AND balance - paid > 0.00"
               See the Where class for a WHERE-clause builder.
           @param args Tuple or mapping of arguments for any placeholders
               you've specified (%s or %(field)s).
               This is primarily for the WHERE clause but may also apply to 
               HAVING.  WHERE always precedes HAVING.
           @param dict boolean True to return each record as a read-write
               dictionary (default).  False to return it as a sequence (DB-API
               standard).
           @param limit int Maximum number of records to return.  None
               (default) means unlimited.  Useful to page through the data or
               to prevent runaway queries.
           @param offset int Offset of first record to return.  0 (default) 
               means no offset.  Useful to page through the data.
           @param group string Entire GROUP BY clause.
           @param having string Entire HAVING clause.
           @param order string Entire ORDER BY clause.
           @param distinct Don't return duplicate rows.  If true, appends
               " DISTINCT" to 'command'.
           @param command string The SQL command, default "SELECT".  Any
               command that returns rows may be used: SHOW, DESCRIBE, etc.
           @param rowcount boolean True to return the number of records
               selected.  The records themselves are not retrieved in this case.
           @return List of dicts (if 'dict' is true), sequence of sequences
               (if 'dict' is false), or int (if 'rowcount' is true).

           Join usage is untested.
        """
        if distinct:
            command += " DISTINCT"
        sql = self.make_sql(command, table, fields, where=where, group=group,
            having=having, order=order, limit=limit, offset=offset)
        return self.query(sql, args, dict=dict, rowcount=rowcount)

    def select_row(self, table, fields, where=None, args=None, dict=True,
        group=None, order=None, default=None):
        """Same as .select() but return a single record.

           @param See .select().
           @param default Returned if no matching record is found.
           @return dict, sequence, or 'default'.
           If multiple records match, only the first is returned.
        """
        records = self.select(table, fields, where=where, args=args,
            group=group, order=None, limit=1, offset=0, dict=dict)
        if records:
            return records[0]
        else:
            return default

    def select_value(self, table, field, where=None, args=None, default=None):
        """Same as select_row() but return a single value in a single record.

           @param field string A single field name or field expression.
           @param table,where,args See .select().
           @param default Returned if no matching record is found.
           @return any The value.
           If multiple records match, only the first is used.
        """
        row = self.select_row(table, [field], where, args, dict=False,
            default=None)
        if row is None:
            return default
        else:
            return row[0]

    def exists(self, table, where=None, args=None):
        """True if a matching row exists, false otherwise."""
        rowcount = self.select(table, ['1'], where=where, args=args,
            limit=1, dict=False, rowcount=True)
        return bool(rowcount)

    def missing(self, table, where=None, args=None):
        """True if a matching row does not exist, false otherwise."""
        return not self.exists(table, where, args)

    def select_column(self, table, field, **kw):
        """Same as .select() but return a list of values for one column.

           @param table string The table name.
           @param field string A field name or field expression.
           @param **kw Any .select() arg that's appropriate, such as 'where'
               and 'args'.
           @return list.
        """
        if 'dict' in kw:
            raise ValueError("keyword arg 'dict' not allowed")
        records = self.select(table, [field], dict=False, **kw)
        return [x[0] for x in records]

    def select_dict(self, table, key_field, value_field, **kw):
        """Return a dictionary based on two columns in the database.

           @param table string The table name.
           @param key_field string The field containing the keys.
           @param value_field string The field containing the values.
           @param **kw Any .select() arg that's appropriate, such as 'where'
               and 'args'.
           @return dict.
        """
        if 'dict' in kw:
            raise TypeError("keyword arg 'dict' is not allowed")
        fields = [key_field, value_field]
        records = self.select(table, fields, dict=False, **kw)
        return dict(records)

    def drop(self, table):
        """Delete the specified table.  Could ruin your day.
        """
        return self.run("DROP TABLE IF EXISTS " + table)

    def create(self, table, field_pairs, indexes='', extra=''):
        """
           @table The table name.
           @field_pairs List of (field name, sql type) strings.  
           @indexes String of extra clauses inside the () in the SQL statement.
           @extra String of extra clauses at the end of the SQL statement.
        """
        self.drop(table)
        sql = self.make_create_sql(table, field_pairs, indexes, extra)
        return self.run(sql)

    def insert(self, table, set_dict, replace=False, literal=None):
        """Insert a record into the database.

           @param table The table name.
           @param set_dict Mapping of field names to field values.
             NOTE: This implementation autoquotes field values, meaning they
             must be literals rather than SQL expressions.  If you need SQL
             expressions, you'll have to use .run() and write the SQL yourself.
           @param replace bool True to do SQL REPLACE instead of SQL INSERT.
             REPLACE automatically deletes any existing row that has the same
             primary key as the new row.  MySQL has Replace; PostgreSQL
             doesn't.
           @param literal String of additional "field=value, field=value"
              items.  This is for values that are SQL expressions, which
              can't be in 'set_dict' or they'd be quoted.
        """
        command = replace and "REPLACE INTO" or "INSERT INTO"
        sql = self.make_iru_sql(command, table, set_dict, literal=literal)
        cursor = self.get_cursor()
        self.execute(cursor, sql, set_dict)
        return cursor.lastrowid

    def update(self, table, set_dict, where, args=None, literal=None):
        """Update database records.

           @param table string The table name.
           @param set_dict Mapping of field names to new field values.
             (The fields to update.)
             NOTE: This implementation autoquotes field values, meaning they
             must be literals rather than SQL expressions.  If you need SQL
             expressions, you'll have to use .run() and write the SQL yourself.
           @param where string Expression specifying which records to modify.
             Pass None to modify all records.  (You must pass this explicitly
             here even though it's the default for other methods, to prevent
             accidentally modifying more records than you intend.)
           @param args Values to plug into the WHERE expression only.
             This is done *separately* from the 'set_dict' argument.
           @param literal String of additional "field=value, field=value"
              items.  This is for values that are SQL expressions, which
              can't be in 'set_dict' or they'd be quoted.
           @return int Count of affected rows.
        """
        if where is not None and args is not None:
            where = self.interpolate(where, args)
        sql = self.make_iru_sql("UPDATE", table, set_dict, where,
            literal=literal)
        return self.run(sql, set_dict)

    def delete(self, table, where, args=None):
        """Delete database records.
        
           @param table string The table name.
           @param where string An expression specifying which records to
               delete.  Pass None to delete all records.  (You must pass this
               explicitly here even though it's the default for other methods,
               to prevent accidentally deleting more records than you
               intended.)
           @param args Values to plug into the WHERE expression.
           @return int Affected row count.  This may be bogus; e.g., MySQL
               returns 0 if all records are deleted.
        """
        sql = self.make_sql('DELETE', table, where=where)
        return self.run(sql, args)

    def tables(self):
        """Return a list of the tables in the database."""
        records = self.query("SHOW TABLES")
        return [x[0] for x in records]

    def describe_table(self, table, dict=False):
        """Return a bunch of information about the table.
        """
        sql = "DESCRIBE " + table
        return self.query(sql, dict=dict)

# These are the subclasses you'd probably use in an application.
class DBAPI_Wrapper(SQLBuilderMixin, Database):  pass
class MySQLdb_Wrapper(SQLBuilderMixin, MySQLDatabase):    pass

#### WHERE CLASS ####
class Where:
    """WHERE expression builder
    
       This class builds a SQL WHERE expression from HTTP GET/POST input in
       an search form in an OO manner.  Example:

       where = dbutil.Where(queryDict)
       where.equal('foo')   
       where.substring('bar', 'barn')  
       where.comparision('baz', '>=')  
       where.relation('relation')  
       dbutil.select(..., where=where, ...)

        'queryDict' is any mapping that represents what the user entered on the
        search form.  E.g., a Quixote Form object, Quixote request.form dict,
        Webware trans.request().fields() dict.  cgi.FieldStorage cannot be
        used directly but you can convert it to a dict:
        dict([(x, fs.getvalue(x)) for x in fs.keys()])

        Note: Don't get confused by the multiple meanings of "query" and
        "field".  In SQL, a query is a SQL statement that returns a result
        rather than performing an action; e.g., SELECT.  In HTTP, a "query
        string" represents extra input parameters supplied with the URL
        request.  A "form field" means one of these parameters, which came from
        a search form and represents one criterion.  A "database field" means
        the corresponding field in the database.

       The example above assumes the following criteria:
       1) Database field 'foo' matches form field 'foo'.  This is useful for
          HTML select lists, numbers, and exact string matches.
       2) Database field 'barn' contains a substring that matches the value of
          form field 'bar'.  This is useful for most text search fields.
       3) Database field 'baz' is <= form field 'baz'.  (The comparision is
          inverted here because the database field is on the left.)  This is
          useful in special circumstances.
       4) If form field 'relation' is 'or', only one of the above criteria
          must match.  If it's anything else, all the criteria must match.
       5) If any of the form fields has a blank value, that criteria is
          disabled.  For instance, if the user leaves the 'baz' control
          blank, database field 'baz' is not looked at.


       Other criteria methods not in the example:
       .in_list() allows a multiple-value criteria, one of which the field must
       match.

       There are supposed to be date methods too but they aren't implemented
       yet:
       .date() : Is the database field the same date as the form field?
       .date_range() : Is the database date in the specified range?
       .date_since() : Is the database date more recent than the form date?
       .interval_since() : Is the database date more recent than N days ago?

       Note that a missing key in queryDict may or may not be an error
       depending on the type of mapping.  Most mappings are a direct
       conversion of the user's query string, so a missing key merely means
       the user left the field blank.  However, for a Quixote Form object a
       missing key means the programmer forgot a widget or misspelled the
       widget's name.  This class was originally made for Quixote Form so
       it raises KeyError if a key is missing.  For other mappings, set class
       attribute '.errorIfKeyMissing' to False, and missing values will be
       silently converted to '' or [].
    """
    errorIfMissingKey = True

    def __init__(self, queryDict):
        self.queryDict = queryDict
        self.parts = []
        self.and_ = True

    def __str__(self):
        """Return the complete WHERE expression we've built so far.
           
           If there are no expression parts, return a bogus expression that's
           always true.  This avoids the surrounding code having to
           special-case it.
        """
        if not self.parts:
            return "(1=1)"  # Expression that's always true.
        sep = self.and_ and " AND " or " OR "
        parts = ["(%s)" % x for x in self.parts]
        return '(' + sep.join(parts) + ')'

    def __repr__(self):
        return "<%s builder for %r>" % (self.__class__.__name__, self.parts)

    def _lookup(self, key, default=''):
        """Look up a field in the queryDict.
        
           @param key Field name.
           @param default Value to return if the real value is '', None, or [].
           @return .queryDict[key], or default.
           @exc KeyError If the key is missing and .errorIfMissingKey is true.
               (If .errorIsMissingKey is false, return the default.)
        """
        try:
            value = self.queryDict[key]
        except KeyError:
            if self.errorIfMissingKey:
                raise
            return default
        if value in [None, []]:
            return default
        return value

    def relation(self, field):
        """Parse query field 'field' for "AND" or "OR" relation."""
        value = self._lookup(field)
        self.and_ = value.lower() != 'or'
        debugWhere(".relation(%r) -> %s", field, self.and_ and "AND" or "OR")

    def exact(self, field, sql_field=None):
        """This SQL field must equal the query field's value."""
        # Pass 'field' not 'value', since .compare() will look it up.
        self.compare(field, '=', sql_field)

    def compare(self, field, operator, sql_field=None):
        """This SQL field must OPERATOR the query field's value."""
        if operator not in COMPARE_OPERATORS:
            raise ValueError("%r is not a comparision operator" % operator)
        if sql_field is None:
            sql_field = field
        debugPrefix = ".compare(%r, %r, %r) -> " % (field, operator, sql_field)
        value = self._lookup(field)
        if not value:
            debugWhere(debugPrefix + "skipping")
            return
        tup = sql_field, operator, escape(value)
        part = "%s %s '%s'" % tup
        self.parts.append(part)
        debugWhere(debugPrefix + `[part]`)

    def substring(self, field, sql_field=None):
        """This SQL field must contain the query field's value as a 
           substring.
        """
        if sql_field is None:
            sql_field = field
        debugPrefix = ".substring(%r, %r) -> " % (field, sql_field)
        value = self._lookup(field)
        if not value:
            debugWhere(debugPrefix + "skipping")
            return
        part = like(sql_field, value)
        self.parts.append(part)
        debugWhere(debugPrefix + `[part]`)

    def in_list(self, field, sql_field=None):
        """This SQL field must contain one of the values listed in the
           query field.
        """
        if sql_field is None:
            sql_field = field
        debugPrefix = ".inList(%r, %r) -> " % (field, sql_field)
        values = self._lookup(field, [])
        if not values:
            debugWhere(debugPrefix + "skipping")
            return
        choices = ", ".join(["'%s'" % escape(x) for x in values])
        part = "%s IN (%s)" % (sql_field, choices)
        self.parts.append(part)
        debugWhere(debugPrefix + `[part]`)

    def date(self, *args, **kw):
        raise NotImplementedError()

    date_range = date_since = interval_since = date

