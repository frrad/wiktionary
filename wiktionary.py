#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import xmltodict
import bz2
import re
import json
import sqlite3
conn = sqlite3.connect('example.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE dictionary
             (language text, word text, part_of_speech text, data text)''')

counter = 0
cutoff = 1000
new_pos = dict()


language_list = ['English', 'French', 'Polish', 'Russian',
                 'Bulgarian', 'Afrikaans', 'Hebrew', 'German',
                 'Italian', 'Dutch', 'Esperanto', 'Finnish',
                 'Korean', 'Spanish', 'Chinese', 'Swedish',
                 'Translingual', 'Japanese', 'Portuguese',
                 'Danish', 'Interlingua', 'Latin',
                 'Catalan', 'Icelandic', 'Albanian', 'Belarusian',
                 'Macedonian', 'Indonesian', 'Middle English',
                 'Wik-Mungkan', 'Sranan Tongo', 'Jersey Dutch',
                 'Marshallese', 'Aragonese', 'Aromanian', 'Tuvaluan',
                 ' See also ', 'Ladino', 'Mauritian Creole', 'Zazaki',
                 'Limburgish', 'Pennsylvania German', 'Rohingya',
                 'Okinawan', 'Uzbek', 'Breton', 'Old Swedish', 'Cebuano',
                 'Nigerian Pidgin', 'Extremaduran', 'Pali',  'Quechua',
                 'Ligurian', 'Ama', 'External links', 'Elfdalian',
                 'Templates', 'Hiligaynon', 'Dutch Low Saxon',
                 'Mirandese', 'Old Dutch',  'Mapudungun',
                 'Maltese', 'Zulu', 'Old Frisian', 'Hawaiian',
                 'Veps', 'Samoan', 'North Frisian',
                 'Greek', 'Old Portuguese', 'Old High German',
                 'Interlingue', 'Livonian', 'Istriot', 'Maori',
                 'Cornish', 'Walloon', 'Navajo', 'Friulian',
                 'Neapolitan', 'Lower Sorbian', 'Haitian Creole',
                 'Classical Nahuatl', 'Dalmatian', 'Basque', 'Fala',
                 'Chuukese', 'Tagalog', 'Lithuanian',
                 'Estonian', 'Slovak', 'Ewe', 'Kurdish',
                 'German Low German', 'Crimean Tatar', 'Turkmen',
                 'Manx', 'Occitan', 'Tahitian',
                 'Norwegian Bokm\xc3\xa5l', 'Scots', 'Serbo-Croatian',
                 'Romanian', 'Old French', 'Faroese', 'Old Saxon',
                 'Ladin', 'Mandarin', 'Malay', 'Luxembourgish', 'Irish',
                 'Ido', 'Asturian', 'Slovene', 'Latvian', 'Welsh',
                 'Norwegian', 'Czech', 'Vietnamese', 'Old English',
                 'Volap\xc3\xbck',  'Middle French', 'Galician',
                 'Lojban', 'Hungarian', 'Norman', 'Turkish',
                 'Norwegian Nynorsk', 'Fijian',
                 'Papiamentu', 'Upper Sorbian', 'Egyptian',
                 'Acehnese', 'Old Norse', 'Zhuang', 'Somali',
                 'Saterland Frisian', 'Alemannic German', 'Rapa Nui',
                 'Hausa', 'Low German', 'Torres Strait Creole',
                 'Tatar', 'Romani', 'Skolt Sami', 'Ossetian',
                 'Northern Sami', 'Old Proven\xc3\xa7al',
                 'Swahili', 'Middle Dutch', 'Gothic', 'Venetian',
                 'Azeri', 'Novial', 'Tok Pisin', 'Romansch', 'Old Irish',
                 'West Frisian', 'Scottish Gaelic', 'Cantonese',
                 'Ukrainian', 'Sicilian', 'Middle Chinese',
                 'German Sign Language', 'Old Spanish', 'Tongan']
languages = dict()
for lang in language_list:
    languages[lang] = 0

pos_list = ['Noun', 'Verb',  'Article', 'Interjection', 'Initialism',
            'Abbreviation', 'Conjunction',  'Preposition', 'Pronoun',
            'Adverb', 'Adjective', 'Proper noun', 'Verb', 'Contraction',
            'Participle', 'Prefix', 'Suffix', 'Phrase', 'Particle']
parts_of_speech = dict()
for pos in pos_list:
    parts_of_speech[pos] = 0


new_lang = dict()


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

    title = item['title']
    raw = item[u'revision']['text']['#text']

    tree = build_tree(raw.split('\n'))
    process_tree(title, tree)

    if counter % 100 == 0:
        print counter
        print 100 * float(counter) / cutoff

    if counter > cutoff:
        return False

    return True


def build_tree(string_list):
    output = dict()
    index = []
    height = 100

    for i, line in enumerate(string_list):
        if not header(line):
            continue
        (n, title) = header(line)
        if n <= height:
            height = n
            index.append((i, n, title))

    indax = [entry for entry in index if entry[1] == height]

    if len(indax) == 0:
        return '\n'.join(string_list).strip('\n')

    # Untitled prefix
    if indax[0][0] > 0:
        output[''] = build_tree(string_list[:indax[0][0]])
    # Tail
    output[indax[-1][2]] = build_tree(string_list[indax[-1][0] + 1:])

    # No intermediate piece
    if len(indax) == 1:
        return output

    for rg in zip(indax[:-1], indax[1:]):
        title = rg[0][2]
        a, b = rg[0][0], rg[1][0]
        output[title] = build_tree(string_list[a + 1:b])

    return output


header_cache = dict()


# If string is formatted ===Header=== return (#='s, 'Header') otherwise False
def header(string):
    if len(string) == 0 or string[0] != '=':
        return False
    if string in header_cache:
        return header_cache[string]

    m = re.match("(=*)([^=]*)(=*)$", string)
    if m is not None:
        if len(m.group(1)) == 0 or m.group(1) != m.group(3):
            header_cache[string] = False
            return False
        else:
            header_cache[string] = (len(m.group(1)), m.group(2))
            return (len(m.group(1)), m.group(2))
    header_cache[string] = False
    return False


def summarize(entry):
    if type(entry) == type(dict()):
        if '' in entry:
            return summarize(entry[''])
        else:
            return ''

    entry = re.sub(r'\[\[([^\|\]]*)\|([^\|\]]*)\]\]', lambda x: x.group(2), entry)
    entry = re.sub(r'\[\[([^\|\]]*)\]\]', lambda x: x.group(1), entry)
    entry = re.sub(r'{{(([^|}]+)\|)+([^|}]+)}}', lambda x:  x.group(3), entry)

    return entry


def process_tree(title, tree):
    global languages, new_lang
    for language in tree:
        if language not in languages:
            new_lang[language] = new_lang.get(language, 0) + 1
            continue
        languages[language] += 1
        for part_of_speech in tree[language]:
            if part_of_speech not in parts_of_speech:
                new_pos[part_of_speech] = new_pos.get(part_of_speech, 0) + 1
                continue
            parts_of_speech[part_of_speech] += 1
            entry = tree[language][part_of_speech]

            print '\n\n\n\n\n', title.encode('utf-8'), language, part_of_speech, '\n============'
            print summarize(entry).encode('utf-8')
            print '============\n\n\n\n\n'

            store(language, title, part_of_speech, json.dumps(
                entry))


def store(language, word, part_of_speech, data):
    # Insert a row of
    c.execute("INSERT INTO dictionary VALUES (?,?,?,?)",
              (language, word, part_of_speech,  data))


with bz2.BZ2File('enwiktionary-latest-pages-articles.xml.bz2', 'r') as f:
    try:
        xmltodict.parse(f, item_depth=2, item_callback=handle)
    except xmltodict.ParsingInterrupted:
        print 'hit max number of entries to process'

# Save (commit) the changes
conn.commit()
# Close connection
conn.close()
print languages, parts_of_speech
print '=========='
print new_pos, new_lang
