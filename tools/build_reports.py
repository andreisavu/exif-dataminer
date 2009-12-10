#! /usr/bin/env python

import sys

import mapper

class ExifReport(mapper.Job):

    def map(self, photo):
        seen = set()
        for tag, _, value in photo['exif']:
            if tag not in seen and value is not None and type(value) != list:
                seen.add(tag)
                yield tag, value

    def reduce(self, key, values):
        yield { 'tag' : key, 
            'count' : len(values),
            'values' : self.distinct_sorted_by_freq(values)
        }

    def distinct_sorted_by_freq(self, values):
        result = {}
        for v in values:
            if v in result:
                result[v] += 1
            else: 
                result[v] = 1
        result = sorted(result.items(), cmp=lambda a,b: cmp(a[1], b[1]), reverse=True)
        return [list(el) for el in result]
        

def main():
    
    mapper.db['exif_tags'].remove({})
    mapper.run(
        mapper.db['photos'].find({'exif':{'$ne':[]}}),
        mapper.db['exif_tags'],
        ExifReport())


if __name__ == '__main__':
    sys.exit(main())

