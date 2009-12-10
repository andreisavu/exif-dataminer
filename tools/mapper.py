""" MongoDB collection iterator """

from pymongo.connection import Connection
from settings import MONGO

db = Connection(MONGO['host'], MONGO['port'])[MONGO['db']]

class Job(object):
    """ Pseudo map/reduce job interface class """

    def map(self, element):
        """ This function is called for each element of the collection

        It should yield (key, value) pairs
        """
        raise TypeError('Not implemented.')

    def reduce(self, key, values):
        """ This function will be called with all the values attached to a key 

        It should yield elements that are going to be part of the result collection.
        """
        raise TypeError('Not implemented.')

def run(src, out, job):
    """ Run mapreduce job on mongo collection. 

    The results are saved to out collection """
    mr = _run_mapper(src, job.map)
    for key in mr.iterkeys():
        map(out.save, filter(None, job.reduce(key, mr[key])))

def _run_mapper(cursor, mapfn):
    """ Run a map function over a collection and acumulate the results in memory """
    mr = {}
    for element in cursor:
        for key, value in mapfn(element):
            if key in mr: mr[key].append(value)
            else: mr[key] = [value]
    return mr
    
