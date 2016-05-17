#!/usr/bin/env python
# -*- coding: utf-8 -*-


import xmltodict
import bz2

counter = 0
cutoff = 1000000
languages = {'English': 0, 'French': 0, 'Polish': 0, 'Russian': 0,
             'Bulgarian': 0, 'Afrikaans': 0, 'Hebrew': 0, 'German': 0,
             'Italian': 0, 'Dutch': 0, 'Esperanto': 0, 'Finnish': 0,
             'Korean': 0, 'Spanish': 0, 'Chinese': 0, 'Swedish': 0,
             'Translingual': 0, 'Japanese': 0, 'Portuguese': 0,
             u'Volapük': 0, 'Danish': 0, 'Interlingua': 0, 'Latin': 0,
             'Catalan': 0, 'Icelandic': 0, 'Albanian': 0, 'Belarusian': 0,
             'Macedonian': 0, 'Indonesian': 0, 'Middle English': 0}


def handle(path, item):
    global counter, languages
    counter += 1

    # Not a word / otherwise malformed
    if 'title' not in item:
        return True
    if 'revision' not in item:
        return True
    if 'text' not in item['revision']:
        return True
    if '#text' not in item['revision']['text']:
        return True

    data = parse_rev(item[u'revision']['text']['#text'])
    if not data:
        return True

    languages[data['language']] += 1

    if counter % 1000 == 0:
        print 100 * float(counter) / cutoff, languages

    if counter > cutoff:
        return False

    return True


def parse_rev(info):
    global languages
    data = dict()

    for line in info.split('\n'):
        if line[:2] == '==' and 'language' not in data:
            data['language'] = line[2:-2]
            break

    if 'language' not in data:
        return False
    if data['language'] not in languages:
        return False

    return data

with bz2.BZ2File('enwiktionary-latest-pages-articles.xml.bz2', 'r') as f:
    try:
        xmltodict.parse(f, item_depth=2, item_callback=handle)
    except xmltodict.ParsingInterrupted:
        print languages
