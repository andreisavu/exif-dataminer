#! /usr/bin/env python

import sys

import mapper

class ExifReport:
    def map(self, photo):
        for tag, label, _ in photo['exif']:
            yield (tag, label), 1

    def reduce(self, key, values):
        tag, label = key
        return {
            'tag' : tag, 
            'label' : label, 
            'count' : len(values)
        }

def main():
    
    exif_report = ExifReport()
    mapper.db['exif_tags'].remove({})
    mapper.run(
        mapper.db['photos'].find({'exif':{'$ne':[]}}),
        mapper.db['exif_tags'],
        exif_report.map,
        exif_report.reduce)


if __name__ == '__main__':
    sys.exit(main())

