# CardMaker

Python tool for making Anki cards from JMdict and KanjiDic2 queries. It leverages code from Tarek Saier's fantastic [`anki_add_pitch`](https://github.com/IllDepence/anki_add_pitch) to add pitch accent information.

## Kanji queries

For `char` (kanji) queries, the corresponding card has the kanji at the front and on'yomi and kun'yomi readings at the back, plus meanings.

### Example

```
> ? char はや
[1] 鮠:17:dace (carp),(kokuji)
[2] 鰷:22:minnow
[3] 早:6:early,fast
[4] 甲:5:armor,high (voice),A grade,first class,former,instep,carapace
[5] 矢:5:dart,arrow
[6] 兄:5:elder brother,big brother
> ? [1-6/no] (1)
```

## Vocabulary queries

For vocabulary entry queries, corresponding recognition and recall cards are created. Furigana is obtained from the [JmdictFurigana project](https://github.com/Doublevil/JmdictFurigana). For recognition cards, you can tap on the kanji form to show the furigana (inspired by [this repo](https://github.com/coolmule0/JLPT-N5-N1-Japanese-Vocabulary-Anki)).

### Example

```
> ? はやい
[1] はやい (早い) : 1. fast/quick/hasty/brisk 2. early (in the day, etc.)/premature 3. (too) soon/not yet/(too) early 4. easy/simple/quick
> ? [1-1/no] (1)
```

## Dependencies

- [Jamdict](https://github.com/neocl/jamdict)
- [genanki](https://github.com/kerrickstaley/genanki)
- [The latest JmdictFurigana file](https://github.com/Doublevil/JmdictFurigana/releases/latest). You can download it by doing `bash get_JmdictFurigana.sh`.

