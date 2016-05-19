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

    if filter_out(raw):
        return True

    tree = build_tree(raw.split('\n'))
    # print '\n\n\n\n', tree
    process_tree(title, tree)

    if counter % 100 == 0:
        print 100 * float(counter) / cutoff

    if counter > cutoff:
        return False

    return True


def build_tree(string_list):
    output = dict()
    pushdown = []
    height = -1
    pushdown_label = ''

    for line in string_list:
        headed = False
        if header(line):
            (n, label) = header(line)
            if height == -1 or height == n:
                if pushdown_label != '' or pushdown != []:
                    output[pushdown_label] = build_tree(pushdown)
                height, pushdown_label, pushdown = n, label, []

                headed = True

        if not headed and line != '':
            pushdown += [line]

    if height == -1 and pushdown != []:
        return '\n'.join(pushdown)

    if pushdown_label != '' or pushdown != []:
        output[pushdown_label] = build_tree(pushdown)

    return output


# If string is formatted ===Header=== return (#='s, 'Header') otherwise False
header_cache = dict()


def header(string):
    if len(string) == 0 or string[0] != '=':
        return False
    if string in header_cache:
        return header_cache[string]

    m = re.match("(=*)([^=]*)(=*)$", string)
    if m is not None:
        if len(m.group(1)) == 0:
            header_cache[string] = False
            return False
        if m.group(1) != m.group(3):
            header_cache[string] = False
            return False
        else:
            header_cache[string] = (len(m.group(1)), m.group(2))
            return (len(m.group(1)), m.group(2))
    header_cache[string] = False
    return False


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
            store(language, title, part_of_speech, json.dumps(
                entry))


def store(language, word, part_of_speech, data):
    # Insert a row of data
    c.execute("INSERT INTO dictionary VALUES (?,?,?,?)",
              (language, word, part_of_speech,  data))


def filter_out(raw):
    return False
    for i, line in enumerate(raw.split('\n')):
        if i > 5:
            return True
        if header(line):
            (_, lang) = header(line)
            if lang == 'Korean':
                return False
    return True

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
