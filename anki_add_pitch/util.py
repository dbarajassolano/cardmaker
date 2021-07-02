"""
MIT License

Copyright (c) 2019 Tarek Saier

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
""" Utility functions used in both extend and remove script.
"""

import json

def select_deck(c, msg):
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('{} (enter the number)'.format(msg))

    for i in range(len(decks)):
        print(' [{}] {}'.format(i, decks[i][1]))
    inp = int(input(''))
    return decks[inp][0]

def get_note_ids(c, deck_id):
    note_ids = []
    for row in c.execute('SELECT id FROM notes WHERE id IN (SELECT nid FROM'
                          ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
        nid = row[0]
        note_ids.append(nid)
    return note_ids

def select_note_fields(c, note_id):
    example_row = c.execute(
        'SELECT flds FROM notes WHERE id = ?', (note_id,)
        ).fetchone()
    example_flds = example_row[0].split('\x1f')
    for i in range(len(example_flds)):
        if len(example_flds[i]) > 0:
            print(' [{}] {}'.format(i, example_flds[i][:20]))
    print('Select the field containing the Japanese expression. (enter the number) ')
    expr_idx = int(input(''))
    print('Select the field containing the reading. (enter the number) ')
    reading_idx = int(input(''))
    return expr_idx, reading_idx
