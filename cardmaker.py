from CM import VocabEntry, VocabNote, KanjiEntry, KanjiNote
import genanki
import random
import re
import argparse

saved_to_collection = False
exit_flag = False

deck_id      = random.randrange(1 << 30, 1 << 31)
style = """
.card {
 font-size: 20px;
 text-align: center;
}
.kanji {
 font-size: 40px;
}
.pos {
 font-size: 10px;
 font-style: italic;
}
.pitchbox {
 padding-top: 10px;
}
ruby {
  display: inline-flex;
  flex-direction: column-reverse;
}
rb, rt {
  display: inline;
  line-height: 1;
}
"""

model_gen    = random.Random(0)

kanji_fields    = [{'name': 'Question'}, {'name': 'Answer'},]
kanji_templates = [{'name': 'Kanji card', 'qfmt': '<p class="kanji">{{Question}}</p>', 'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',},]
kanji_model     = genanki.Model(model_gen.randrange(1 << 30, 1 << 31), 'Kanji note model', fields=kanji_fields, templates=kanji_templates, css=style)

vocab_fields    = [{'name': 'KanjiFormFuriganized'}, {'name': 'KanaForm'}, {'name':'Meanings'}, {'name': 'Pitch'}]
vocab_templates = [{'name': 'Recognition', 'qfmt': '<p class="kanji">{{KanjiFormFuriganized}}</p>', 'afmt': '{{FrontSide}}<hr id="answer">{{KanaForm}}<br>{{Meanings}}<div class=pitchbox>{{Pitch}}</div>',}, {'name': 'Recall', 'qfmt': '<p>{{Meanings}}</p>', 'afmt': '{{FrontSide}}<hr id="answer"><p class="kanji">{{KanjiFormFuriganized}}</p>{{KanaForm}}<div class=pitchbox>{{Pitch}}</div>',}]
vocab_model     = genanki.Model(model_gen.randrange(1 << 30, 1 << 31), 'Vocab note model', fields=vocab_fields, templates=vocab_templates, css=style)


parser = argparse.ArgumentParser(description='Make Anki cards from JMDict/KanjiDic2 searches')
parser.add_argument('collection', metavar='C', type=str, nargs=1, help='Collection filename')
parser.add_argument('--deck', dest='deck_name', action='store', type=str, nargs='?', default='CardMaker deck', const='CardMaker deck', help='Deck name')
args = parser.parse_args()
outfile = args.collection[0]
deck_name = args.deck_name
try:
    if not isinstance(outfile, str) or not outfile:
        print('Invalid output file name')
        quit()
except TypeError as exc:
    print('Invalid output file name')
    quit()

deck = genanki.Deck(deck_id, deck_name)

print(deck_name)

notes = []

edit_pattern   = re.compile(r'^edit [0-9]+$')
delete_pattern = re.compile(r'^delete [0-9]+$')
char_pattern   = re.compile(r'^char (.*)')

if __name__ == '__main__':

    while exit_flag == False:
    
        command = input('> ? ')
        command = command.encode('utf-8', 'replace').decode()
        
        if command == 'exit':
            if saved_to_collection == False:
                command = input('> Nothing was saved to a collection. Are you sure [y/n]? ')
                if command == 'y':
                    exit_flag = True
                    continue
                else:
                    continue

        elif command == 'list':
            idx = 1
            print('')
            if notes == []:
                print('No notes yet')
            for note in notes:
                print('* Note #{:d}'.format(idx))
                print(note.short())
                idx = idx + 1
            print('')

        elif command == 'save':
            if notes == []:
                print('Nothing to save yet')
            else:
                for note in notes:
                    if note.is_kanjinote:
                        note = genanki.Note(model=kanji_model, fields=[note.question, note.answer])
                    else:
                        note = genanki.Note(model=vocab_model, fields=[note.kanji_form_furiganized, note.kana_form, note.meanings, note.pitch_svg])
                    deck.add_note(note)
                genanki.Package(deck).write_to_file(outfile)
                exit_flag = True
            continue

        elif delete_pattern.search(command):
            idx = int(re.findall("[0-9]+", command)[0]) - 1
            try:
                del notes[idx]
            except IndexError:
                print(f'Invalid note number (Valid: 1-{len(notes)})')
                continue

        elif not command:
            continue

        else:
            # Determine if you want to edit a note
            replace_idx = None
            if edit_pattern.search(command):
                replace_idx = int(re.findall("[0-9]+", command)[0]) - 1
                if replace_idx >= len(notes):
                    print(f'Invalid note number (Valid: 1-{len(notes)})')
                    continue
                command = input('> New search? ')
                command = command.encode('utf-8', 'replace').decode()
            if char_pattern.search(command):
                # Kanji chard
                char = KanjiEntry(char_pattern.search(command).groups()[0])
                if char.kanjidic_char == None:
                    continue
                note = KanjiNote(char)
            else:
                # Vocabulary note
                entry = VocabEntry(command)
                if entry.jmdict_entry == None:
                    continue
                note = VocabNote(entry)
            # Replace existing note
            if replace_idx is not None:
                notes[replace_idx] = note
                print(f'\n{notes[replace_idx]}\n')
            else:
                # Add new note to list of notes
                notes.append(note)
                print(f'\n{notes[-1]}\n')


quit()
