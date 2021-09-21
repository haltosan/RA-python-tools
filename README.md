# RA-python-tools
Tools written in python for file analysis and name extraction.
The main file is 'file analysis.py' which has all the tools I use.
'predicates.py' has predicate functions I wrote to help identify data that is either useful or useless.
Each file has it's own documentation in a block comment, but feel free to yell at me if something doesn't make sense.



### Usage

Download the latest release and extract the zip. Inside are a few python files. The main file is file_analysis.py (it has all the functions defined). The other files are either exteneded features (experimental) or supporting files (predicates). My prefered usage is opening file_analysis.py in IDLE and running it. There isn't any output (aside from working directory), but it has all the functions loaded and ready to use from the shell.

```
>>> raw = get("example.txt")
>>> raw
['this', 'is', 'a', 'bucket']
```

Another way to use this is to import file_analysis in another project and use the functions.
```
import file_analysis as f
import predicates as p

rawFile = f.get("example.txt")
print(cleanFile(rawFile, p.long))
```

Visit the [wiki](https://github.com/haltosan/RA-python-tools/wiki) for syntax and usage.

I also have a help video [here](https://youtu.be/f5S-SsI30pw), but the wiki is far more extensive. Reach out if there are any questions.
