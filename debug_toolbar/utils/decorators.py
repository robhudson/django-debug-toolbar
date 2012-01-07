"""
Useful debugging decorators.
"""
import re, time
from django.conf import settings
from django.db import connection
from django.utils.termcolors import colorize

DEBUG = getattr(settings, 'DEBUG', False)


def print_queries(regex=None):
    """ Print all queries executed in the wrapped function.
        @print_queries('optional_filter_regex')
        def function_with_queries():
            # Do something here that runs some Django queries
            # Perhaps just wrap your page view
    """
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            if DEBUG:
                sqltime = 0.0             # Total time spent running SQL queries
                longest = 0.0             # Longest time spent on a single query
                numshown = 0              # Number of queries diusplayed after filter
                initqueries = 0           # Initial length of connection.queries
                starttime = time.time()   # Time we started this function call
                result = func(*args, **kwargs)
                runtime = round(time.time() - starttime, 3)
                # Print new entries in connection.queries
                for query in connection.queries[initqueries:]:
                    querytime = float(query['time'].strip('[s]'))
                    sqltime += querytime
                    longest = max(longest, querytime)
                    if not regex or re.search(regex, query['sql']):
                        querystr = colorize('\n[%ss] ' % query['time'], fg='yellow')
                        querystr += colorize(query['sql'], fg='blue')
                        print querystr
                        numshown += 1
                # Print summary including total queries, longest, etc..
                numqueries = len(connection.queries) - initqueries
                numhidden = numqueries - numshown
                proctime = round(runtime - sqltime, 3)
                print colorize("------", fg='blue')
                print colorize('Total Time:  %ss' % runtime, fg='yellow')
                print colorize('Proc Time:   %ss' % proctime, fg='yellow')
                print colorize('Query Time:  %ss (longest: %ss)' % (sqltime, longest), fg='yellow')
                print colorize('Num Queries: %s (%s hidden)\n' % (numqueries, numhidden), fg='yellow')
            return result
        return wrapper2
    return wrapper1
