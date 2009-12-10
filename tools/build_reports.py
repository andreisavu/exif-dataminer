#! /usr/bin/env python

import sys

import mapper

class ExifReport(mapper.Job):
    def map(self, photo):
        for tag, label, _ in photo['exif']:
            yield (tag, label), 1

    def reduce(self, key, values):
        tag, label = key
        yield {
            'tag' : tag, 
            'label' : label, 
            'count' : len(values)
        }

def main():
    
    mapper.db['exif_tags'].remove({})
    mapper.run(
        mapper.db['photos'].find({'exif':{'$ne':[]}}),
        mapper.db['exif_tags'],
        ExifReport())


if __name__ == '__main__':
    sys.exit(main())

