from jamdict import Jamdict
import anki_add_pitch.anki_add_pitch as aap
from anki_add_pitch.draw_pitch import pitch_svg
import re
import json
import csv

jam = Jamdict()

def get_jmdict_furigana():
    with open('JmdictFurigana.json', 'r', encoding='utf-8-sig') as jsonfile:
        jmdict_furigana = json.load(jsonfile)
    return jmdict_furigana

def get_N5kanji():
    with open('jlpt_kanji_level_5_base.txt') as csvfile:
        reader = csv.reader(csvfile, skipinitialspace=True)
        N5kanji = [row[0][0] for row in reader]
    return N5kanji

class KanjiEntry:

    def __init__(self, prompt, query_idx=0):
        self.prompt = prompt
        self.kanjidic_char = self.choose_kanjidic_char(query_idx)

    def choose_kanjidic_char(self, query_idx):
        result = jam.lookup(self.prompt)
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

    def __str__(self):
        return self.kanjidic_char.__repr__()

class KanjiNote:

    def __init__(self, char):
        self.is_kanjinote = True
        self.char         = char
        self.literal      = self.char.kanjidic_char.literal
        self.meanings     = ', '.join(self.char.kanjidic_char.meanings(english_only=True))
        self.on_readings  = self.on_readings()
        self.kun_readings = self.kun_readings()
        self.question     = self.literal
        self.answer       = f'On\'yomi {self.on_readings}<br>Kun\'yomi {self.kun_readings}<br>{self.meanings}'

    def on_readings(self):
        tmp = []
        for rm in self.char.kanjidic_char.rm_groups:
            tmp.append(', '.join(reading.value for reading in rm.on_readings))
        return ', '.join(tmp)

    def kun_readings(self):
        tmp = []
        for rm in self.char.kanjidic_char.rm_groups:
            tmp.append(', '.join(reading.value for reading in rm.kun_readings))
        return ', '.join(tmp)

    def __str__(self):
        return f'Literal:\t{self.literal}\nMeanings:\t{self.meanings}\nOn\'yomi:\t{self.on_readings}\nKun\'yomi:\t{self.kun_readings}\nHTML:\t\t{self.question}<hr id="answer">{self.answer}'

    def short(self):
        return f'{self.char.kanjidic_char.__repr__()}'
    

class VocabEntry:
    
    def __init__(self, prompt, query_idx=0):
        self.prompt = prompt
        self.jmdict_entry = self.choose_jmdict_entry(query_idx)
        
    def choose_jmdict_entry(self, query_idx):
        result = jam.lookup(self.prompt)
        if result.entries == []:
            print('Found nothing')
            return None
        for idx in range(len(result.entries)):
            self.print_jmdict_entry(idx + 1, result.entries[idx])
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

    def print_jmdict_entry(self, idx, entry):
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

    def __str__(self):
        return self.jmdict_entry.__str__()
    
class VocabNote:

    acc_dict = aap.get_accent_dict('anki_add_pitch/wadoku_pitchdb.csv')

    def __init__(self, entry):
        self.is_kanjinote = False
        self.entry     = entry
        self.kana_form = self.entry.jmdict_entry.kana_forms[0].text
        self.meaning   = ', '.join(sense.text().capitalize() for sense in self.entry.jmdict_entry.senses)

        # An entry may not have kanji form (like 'もう')
        if self.entry.jmdict_entry.kanji_forms:
            self.kanji_form    = self.entry.jmdict_entry.kanji_forms[0].text
            self.furigana_form = FuriganaForm(self.kanji_form, self.kana_form)
            self.kanji_form_furiganized = self.furigana_form.to_html()
        else:
            self.kanji_form    = ''
            self.furigana_form = ''
            self.kanji_form_furiganized = self.kana_form
            
        self.meanings  = self.make_meanings()
        self.idseq     = self.entry.jmdict_entry.idseq
        self.pitch_svg = self.make_pitch_svg()

    def short(self):
        return f'{self.entry.__str__()}'

    def __str__(self):
        return f'{self.entry.__str__()}\nKanji form:\t{self.kanji_form}\nKana form:\t{self.kana_form}\nMeaning:\t{self.meaning}\nFuriganized:\t{self.furigana_form}\nPitch?:\t\t{True if self.pitch_svg else False}'

    def make_meanings(self):
        tmp = []
        for sense in self.entry.jmdict_entry.senses:
            pos = ' | '.join(pos for pos in sense.pos)
            tmp.append(f'{sense.text().capitalize()}  <span class="pos">{pos}</span>')
        return '<br>'.join(tmp)

    def make_pitch_svg(self):
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
    N5kanji = get_N5kanji()
    
    def __init__(self, kanji_form, kana_form):
        self.kana_form  = kana_form
        self.kanji_form = kanji_form
        self.data = self.furiganize()

    def furiganize(self):
        furigana_data = next((data for data in self.jmdict_furigana if data["text"] == self.kanji_form and data["reading"] == self.kana_form), None)
        if furigana_data == None:
            print('Couldn''t find furigana data')
            return [{'ruby': self.kanji_form, 'rt' : self.kana_form}]
        else:
            ndata = len(furigana_data['furigana'])
            data  = [None] * ndata
            for idx in range(ndata):
                data[idx] = furigana_data['furigana'][idx]
                ruby = data[idx]['ruby']
                if 'rt' in data[idx]:
                    if (all(s in self.N5kanji for s in ruby)):
                        data[idx].pop('rt', None) # Delete 'rt' from furigana data because all kanji are JLPT-N5
        return data

    def __str__(self):
        if self.data == None:
            return ''
        else:
            tmp = []
            for idx in range(len(self.data)):
                tmp.append(self.data[idx]['ruby'])
                if 'rt' in self.data[idx]:
                    tmp[-1] = tmp[-1] + '({})'.format(self.data[idx]['rt'])
            return ''.join(tmp)
           
    def to_html(self):
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
                

        

    

    


