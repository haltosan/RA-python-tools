# RA-python-tools
Tools written in python for file analysis and name extraction.
The main file is 'file analysis.py' which has all the tools I use.
'predicates.py' has predicate functions I wrote to help identify data that is either useful or useless.
Each file has it's own documentation in a block comment, but feel free to yell at me if something doesn't make sense.



### Usage
This is just an example of how I would use this:

`
= RESTART: file analysis.py
>>> raw = get('1924.txt')
>>> cleanRaw = cleanFile(raw, pred = p.long, cleaner = cleanChars, cleanArg = p.nameChar, negatePred = False, negateClean = False)
>>> cleanRaw[:5]
['Abaya, Gonzalo, jr, M, Pagsanjan, Laguna, P I Harry Benjamin, BS, Grad, Olean', 'Abbey, Charles Newell,  Cherry Creek Ager Beatrice, A, Tarrytown', 'Abel, Armand Henry, A, Cleveland, Ohio Allen, Dell Keller, Eng, Dallas, Texas', 'Abel, Charles Allen, g, Buffalo Allen, Floyd Benjamin, M, Elmira', 'Abel, Herri Ernest, MD NYC, Elizabeth, N J Allen, Laura Catherine, Ag, C']
>>> save(cleanRaw, 'example.txt')
`

This example shows me removing all characters that don't belong in a name and any lines that aren't long (longer than 5 chars). I look at the first 5 elements to make sure I like the output, and save it to a file.
