from cards import CMEntry, CMVocabCard, CMChar, CMKanjiCard
import genanki
import random
import re
import argparse

saved_to_collection = False
exit_flag = False

deck_id      = random.randrange(1 << 30, 1 << 31)
fields       = [{'name': 'Question'}, {'name': 'Answer'}, {'name': 'Pitch'},]
fields_np    = [{'name': 'Question'}, {'name': 'Answer'},]
templates    = [{'name': 'Card 1', 'qfmt': '<p class="question">{{Question}}</p>', 'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br><div class=pitchbox>{{Pitch}}</div>',},]
templates_np = [{'name': 'Card 1', 'qfmt': '<p class="question">{{Question}}</p>', 'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',},]
style = """
.card {
 font-size: 20px;
 text-align: center;
}
.question {
 font-size: 40px;
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
model_id     = model_gen.randrange(1 << 30, 1 << 31)
model_np_id  = model_gen.randrange(1 << 30, 1 << 31)
model        = genanki.Model(model_id, 'CardMaker model', fields=fields, templates=templates, css=style)
model_np     = genanki.Model(model_np_id, 'CardMaker model', fields=fields_np, templates=templates_np, css=style)

parser = argparse.ArgumentParser(description='Make Anki cards from JMDict/KanjiDic2 searches')
parser.add_argument('collection', metavar='C', type=str, nargs=1, help='Collection filename')
parser.add_argument('--deck', dest='deck_name', action='store', type=str, nargs=1, default='CardMaker deck', help='Deck name')
args = parser.parse_args()
outfile = args.collection[0]
deck_name = args.deck_name[0]
try:
    if not isinstance(outfile, str) or not outfile:
        print('Invalid output file name')
        quit()
except TypeError as exc:
    print('Invalid output file name')
    quit()

print(f'\nWill create deck {deck_name} with id#{deck_id}\n\t...of cards with model id#{model_id}\n\t\t...to file {outfile}\n')

deck = genanki.Deck(deck_id, deck_name)

cards = []

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
            if cards == []:
                print('No cards yet')
            for card in cards:
                print('* Card #{:d}'.format(idx))
                print(card.short())
                idx = idx + 1
            print('')

        elif command == 'save':
            if cards == []:
                print('Nothing to save yet')
            else:
                for card in cards:
                    if not hasattr(card, 'pitch_svg'):
                        note = genanki.Note(model=model_np, fields=[card.question, card.answer])
                    else:
                        if card.pitch_svg:
                            note = genanki.Note(model=model, fields=[card.question, card.answer, card.pitch_svg])
                        else:
                            note = genanki.Note(model=model_np, fields=[card.question, card.answer])
                    deck.add_note(note)
                genanki.Package(deck).write_to_file(outfile)
                exit_flag = True
            continue

        elif delete_pattern.search(command):
            idx = int(re.findall("[0-9]+", command)[0]) - 1
            try:
                del cards[idx]
            except IndexError:
                print(f'Invalid card number (Valid: 1-{len(cards)})')
                continue

        elif not command:
            continue

        else:
            # Determine if you want to edit a card
            replace_idx = None
            if edit_pattern.search(command):
                replace_idx = int(re.findall("[0-9]+", command)[0]) - 1
                if replace_idx >= len(cards):
                    print(f'Invalid card number (Valid: 1-{len(cards)})')
                    continue
                command = input('> New search? ')
                command = command.encode('utf-8', 'replace').decode()
            if char_pattern.search(command):
                # Kanji chard
                char = CMChar(char_pattern.search(command).groups()[0])
                if char.kanjidic_char == None:
                    continue
                card = CMKanjiCard(char)
            else:
                # Vocabulary card
                entry = CMEntry(command)
                if entry.jmdict_entry == None:
                    continue
                card = CMVocabCard(entry)
            # Replace existing card
            if replace_idx is not None:
                cards[replace_idx] = card
                print(f'\n{cards[replace_idx]}\n')
            else:
                # Add new card to list of cards
                cards.append(card)
                print(f'\n{cards[-1]}\n')


quit()
