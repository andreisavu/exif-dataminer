""" MongoDB collection iterator utils """

from pymongo.connection import Connection
from settings import MONGO

db = Connection(MONGO['host'], MONGO['port'])[MONGO['db']]

def run(src, out, mapfn, reducefn=None):
    mr = _run_mapper(src, mapfn)
    if reducefn is not None:
        for key in mr.keys():
            out.save(reducefn(key, mr[key]))
    else:
        map(out.save, mr.values())

def _run_mapper(cursor, mapfn):
    map_result = {}
    for element in cursor:
        for key, value in mapfn(element):
            if key in map_result:
                map_result[key].append(value)
            else:
                map_result[key] = [value]
    return map_result
    

