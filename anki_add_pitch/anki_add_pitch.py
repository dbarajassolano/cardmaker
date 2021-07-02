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
""" Add pitch accent indicators to Anki cards.

    Below script makes use of data from Wadoku by Ulrich Apel.
    (See file wadoku_parse.py for more details.)
    Wadoku license information is available on the web:

    http://www.wadoku.de/wiki/display/WAD/Wörterbuch+Lizenz
    http://www.wadoku.de/wiki/display/WAD/%28Vorschlag%29+Neue+Wadoku-Daten+Lizenz
"""

import json
import re
import sqlite3
import sys
import time
from anki_add_pitch.draw_pitch import pitch_svg
from anki_add_pitch.util import select_deck, select_note_fields, get_note_ids

def get_accent_dict(path):
    acc_dict = {}
    with open(path) as f:
        for line in f:
            orths_txt, hira, hz, accs_txt, patts_txt = line.strip().split('\u241e')
            orth_txts = orths_txt.split('\u241f')
            if clean_orth(orth_txts[0]) != orth_txts[0]:
                orth_txts = [clean_orth(orth_txts[0])] + orth_txts
            patts = patts_txt.split(',')
            patt_common = patts[0]  # TODO: extend to support variants?
            if is_katakana(orth_txts[0]):
                hira = hira_to_kata(hira)
            for orth in orth_txts:
                if not orth in acc_dict:
                    acc_dict[orth] = []
                new = True
                for patt in acc_dict[orth]:
                    if patt[0] == hira and patt[1] == patt_common:
                        new = False
                        break
                if new:
                    acc_dict[orth].append((hira, patt_common))
    return acc_dict

def get_acc_patt(expr_field, reading_field, dicts):
    def select_best_patt(reading_field, patts):
        best_pos = 9001
        best = patts[0]  # default
        for patt in patts:
            hira, p = patt
            try:
                pos = reading_field.index(hira)
                if pos < best_pos:
                    best = patt
                    best_pos = pos
            except ValueError:
                continue
        return best
    expr_field = expr_field.replace('[\d]', '')
    expr_field = expr_field.replace('[^\d]', '')
    expr_field = expr_field.strip()
    for dic in dicts:
        patts = dic.get(expr_field, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = expr_field.split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
        guess = re.sub('[<&]', ' ', expr_field).split(' ')[0]
        patts = dic.get(guess, False)
        if patts:
            return select_best_patt(reading_field, patts)
    return False

def hira_to_kata(s):
    return ''.join(
        [chr(ord(ch) + 96) if ('ぁ' <= ch <= 'ゔ') else ch for ch in s]
        )

def is_katakana(s):
    num_ktkn = 0
    for ch in s:
        if ch == 'ー' or ('ァ' <= ch <= 'ヴ'):
            num_ktkn += 1
    return num_ktkn / max(1, len(s)) > .5

def clean_orth(orth):
    orth = re.sub('[()△×･〈〉{}]', '', orth)  # 
    orth = orth.replace('…', '〜')  # change depending on what you use
    return orth
