from __future__ import annotations
from jamdict import Jamdict
from lxml import etree as ET
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import anki_add_pitch.anki_add_pitch as aap
import re
import json
if TYPE_CHECKING:
    from jamdict import jmdict, kanjidic2

jam = Jamdict()

def get_jmdict_furigana() -> list:
    """Read JmdictFurigana.json into a list of dicts."""
    with open(Path(__file__).parent / 'JmdictFurigana.json', 'r', encoding='utf-8-sig') as jsonfile:
        jmdict_furigana = json.load(jsonfile)
    return jmdict_furigana

def get_char(prompt: str, query_idx :int=0) -> Optional[kanjidic2.Character]:
    """Search with Jamdict and return a kanjidic2.Character off a list of
    possible candidates
    """
    result = jam.lookup(prompt)
    if result.chars == []:
        print('Found nothing')
        return None
    for idx in range(len(result.chars)):
        print(f'[{idx + 1}] {result.chars[idx].__repr__()}')
    if query_idx < 0 or query_idx > len(result.chars):
        print('Invalid index')
        return None
    if not query_idx == 0:
        return result.chars[query_idx - 1]
    cancel_flag = False
    while cancel_flag == False:
        command = input('> ? [{:d}-{:d}/no] (1) '.format(1, len(result.chars)))
        if command == 'no':
            return None
        if command == '':
            return result.chars[0]
        try:
            entrynum = int(command)
            return result.chars[entrynum - 1]
        except ValueError:
            print('Please try again')
        except IndexError:
            print('Please try again')

def get_entry(prompt: str, query_idx :int=0) -> Optional[jmdict.JMDEntry]:
    """Search with Jamdict and return a jmdict.JMDEntry off a list of
    possible candidates
    """
    result = jam.lookup(prompt)
    if result.entries == []:
        print('Found nothing')
        return None
    for idx in range(len(result.entries)):
        print_entry(idx + 1, result.entries[idx])
    if query_idx < 0 or query_idx > len(result.entries):
        print('Invalid index')
        return None
    if not query_idx == 0:
        return result.entries[query_idx - 1]
    cancel_flag = False
    while cancel_flag == False:
        command = input('> ? [{:d}-{:d}/no] (1) '.format(1, len(result.entries)))
        if command == 'no':
            return None
        if command == '':
            return result.entries[0]
        try:
            entrynum = int(command)
            return result.entries[entrynum - 1]
        except ValueError:
            print('Please try again')
        except IndexError:
            print('Please try again')

def print_entry(idx: int, entry: jmdict.JMDEntry):
    """Print a jmdict.JMDEntry."""
    tmp = []
    tmp.append('[%s]' % idx)
    if entry.kana_forms:
        tmp.append(entry.kana_forms[0].text)
        if entry.kanji_forms:
            tmp.append("({})".format(entry.kanji_forms[0].text))
        if entry.senses:
            tmp.append(':')
        if len(entry.senses) == 1:
            tmp.append(entry.senses[0].text())
        else:
            for sense, idx in zip(entry.senses, range(len(entry.senses))):
                tmp.append('{i}. {s}'.format(i=idx + 1, s=sense.text()))
    print(' '.join(tmp))

class KanjiNote:
    """Note for a kanji."""
    def __init__(self, char: kanjidic2.Character):
        self.is_kanjinote = True
        self.char         = char
        self.literal      = self.char.literal
        self.meanings     = ', '.join(self.char.meanings(english_only=True))
        self.question     = self.literal
        self.answer       = f'On\'yomi {self.on_readings()}<br>Kun\'yomi {self.kun_readings()}<br>{self.meanings}'
        self.kanjivg      = self.get_kanjivg()

    def on_readings(self) -> str:
        tmp = []
        for rm in self.char.rm_groups:
            tmp.append(', '.join(reading.value for reading in rm.on_readings))
        return ', '.join(tmp)

    def kun_readings(self) -> str:
        tmp = []
        for rm in self.char.rm_groups:
            tmp.append(', '.join(reading.value for reading in rm.kun_readings))
        return ', '.join(tmp)

    def get_kanjivg(self) -> str:
        # PosixPath to str
        tree = ET.parse(str(Path(__file__).parent / "kanjivg-20160426.xml"))
        id = tree.xpath("//g[@kvg:element = '{:s}']/@id".format(self.literal), namespaces={'kvg':'http://kanjivg.tagaini.net'})
        id = next((i for (x, i) in zip([ix.find('-') for ix in id], id) if x < 0), None)
        if id:
            filesvg = 'kanji/' + id[4:] + '.svg'
            filesvg = Path(__file__).parent / filesvg
            with open(filesvg, "r") as myfile:
                data = myfile.read()
                data = data[data.find('<svg'):].replace('\n', '').replace('xmlns="http://www.w3.org/2000/svg" ', '').replace('kvg:', '')
                return data
        else:
            print(f'Couldn\'t find stroke order data for kanji {self.literal}')
            return ''

    def __str__(self) -> str:
        return f'Literal:\t{self.literal}\nMeanings:\t{self.meanings}\nOn\'yomi:\t{self.on_readings()}\nKun\'yomi:\t{self.kun_readings()}\nHTML:\t\t{self.question}<hr id="answer">{self.answer}'

    def short(self) -> str:
        return f'{repr(self.char)}'
    
class VocabNote:

    acc_dict_path = Path(__file__).parent / 'anki_add_pitch/wadoku_pitchdb.csv'
    acc_dict = aap.get_accent_dict(acc_dict_path)

    def __init__(self, entry: jmdict.JMDEntry):
        self.is_kanjinote = False
        self.entry     = entry
        self.kana_form = self.entry.kana_forms[0].text
        self.meaning   = ', '.join(sense.text().capitalize() for sense in self.entry.senses)

        # An entry may not have kanji form (like 'もう')
        if self.entry.kanji_forms:
            self.kanji_form    = self.entry.kanji_forms[0].text
            self.furigana_form = FuriganaForm(self.kanji_form, self.kana_form)
            self.kanji_form_furiganized = self.furigana_form.to_html()
        else:
            self.kanji_form    = ''
            self.furigana_form = ''
            self.kanji_form_furiganized = self.kana_form
            
        self.meanings  = self.make_meanings()
        self.idseq     = self.entry.idseq
        self.pitch_svg = self.make_pitch_svg()

    def short(self) -> str:
        return f'{self.entry.__str__()}'

    def __str__(self) -> str:
        return f'{self.entry.__str__()}\nKanji form:\t{self.kanji_form}\nKana form:\t{self.kana_form}\nMeaning:\t{self.meaning}\nFuriganized:\t{self.furigana_form}\nPitch?:\t\t{True if self.pitch_svg else False}'

    def make_meanings(self) -> str:
        tmp = []
        for sense in self.entry.senses:
            pos = ' | '.join(pos for pos in sense.pos)
            tmp.append(f'{sense.text().capitalize()}  <span class="pos">{pos}</span>')
        return '<br>'.join(tmp)

    def make_pitch_svg(self) -> str:
        if self.kanji_form == '':
            kf = self.kana_form
        else:
            kf = self.kanji_form
        patt = aap.get_acc_patt(kf, self.kana_form, [self.acc_dict])
        if not patt:
            print(f'Couldn\'t find data in the pitch database for expression {self.kanji_form}')
            return ''
        hira, LlHh_patt = patt
        LH_patt = re.sub(r'[lh]', '', LlHh_patt)
        svg = aap.pitch_svg(hira, LH_patt)
        if not svg:
            print(f'Couldn\'t make svg from pitch data')
            return ''
        return svg
    
class FuriganaForm:

    jmdict_furigana = get_jmdict_furigana()
    
    def __init__(self, kanji_form: str, kana_form: str):
        self.kana_form  = kana_form
        self.kanji_form = kanji_form
        self.data = self.furiganize()

    def furiganize(self) -> list:
        furigana_data = next((data for data in self.jmdict_furigana if data["text"] == self.kanji_form and data["reading"] == self.kana_form), None)
        if furigana_data == None:
            print('Couldn''t find furigana data')
            return [{'ruby': self.kanji_form, 'rt' : self.kana_form}]
        else:
            data = furigana_data['furigana']
        return data

    def __str__(self) -> str:
        if self.data == None:
            return ''
        else:
            tmp = []
            for idx in range(len(self.data)):
                tmp.append(self.data[idx]['ruby'])
                if 'rt' in self.data[idx]:
                    tmp[-1] = tmp[-1] + '({})'.format(self.data[idx]['rt'])
            return ''.join(tmp)
           
    def to_html(self) -> Optional[str]:
        if self.data == None:
            return None
        else:
            ndata = len(self.data)
            tmp = ''
            for idx in range(ndata):
                ruby = self.data[idx]['ruby']
                if 'rt' in self.data[idx]:
                    rt = self.data[idx]['rt']
                    tmp = tmp + f'<ruby>{ruby}<rp>(</rp><rt>{rt}</rt><rp>)</rp></ruby>'
                else:
                    tmp = tmp + ruby
            return tmp
                

        

    

    


