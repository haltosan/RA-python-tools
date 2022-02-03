#!/usr/bin/env python
# coding: utf-8

# # NLP with spaCy

# ## Docs (in progress)

# Summary of what this notebook does:
#  - Reads in text from files
#  - Splits text into sections based on a user-specified regex (for example, separates output from different images that are in the same OCR file)
#  - Runs spaCy on each section, which identifies names, dates, and locations in the words (not super well, but decently)
#  - Uses regex to filter through the names and dates and pick out the ones most likely to be relevant (currently, it chooses the first full name and date in the hopes it's the name and death date of the person in the obituary)

# # Imports

# In[1]:


import os
import re
import csv
import sys
import spacy # using for NER (Named Entity Recognition)

# start debugging for encoding errors
import locale


# # Functions/Other Preliminary Code

# ## Read in the lines in the right format

# In[2]:


def pre_process(fname):
    enc = locale.getpreferredencoding()
    with open(fname, encoding=enc) as fin:
        lines = fin.read()
    return lines


# ## Split text by the image it came from
# 
# TODO: define the regex you want to use to split the file into different entries, and turn on/off the option to delete the last string in the list (depending on the format of the input, may always be empty)

# In[3]:


def split_input(text):
    """Splits text into different strings, using a regex as a seperator"""  
    if type(text) is not str:
        raise NotImplementedError
    
    
    
    # PUT TEXT-SPLITTING REGEX HERE
    split_re = r'--- PAGE END ---'
    split_strings = re.split(split_re, text)
    
    # IF EACH SECTION WILL HAVE A MATCH FOR SPLIT_RE AT THE END, RUN THIS TO DELETE THE LAST STRING IN THE LIST (WILL BE EMPTY)
    last_is_empty = True
    if last_is_empty and len(split_strings) > 0:
        del split_strings[-1] # removes empty string at the end
    return split_strings


# ## Give file information
# 
# TODO: name the output file and give paths for the input and output folders

# In[4]:


# GIVE A NAME FOR THE OUTPUT FILE HERE (not a path, just something recognizable)
output_name = "weekend_end"

# Name of the csv file to write to
target = f"{output_name}.csv"

# PUT INPUT FOLDER HERE
INPUT_PATH = r'V:\papers\current\tree_growth\US\Skagit\skagit_obits\2_NLP\input'

# PUT OUTPUT FOLDER HERE
OUTPUT_PATH = r'V:\papers\current\tree_growth\US\Skagit\skagit_obits\2_NLP\output'

os.chdir(OUTPUT_PATH)


# ### (Makes the output replace the previous file, instead of appending to the previous file)

# In[5]:


# Update target file name so that we aren't appending to an existing file
    
if os.path.exists(target):
    i = 1
    name, ext = target.split('.')
    while os.path.exists(f'{name}_{i}.{ext}'):
        i += 1
    target = f'{name}_{i}.{ext}'

# (took out code for the check file; don't know how to create one with this method


# # Define Regex
# Go to https://regex101.com/ to test your regex. Currently, this notebook needs a regular expression for death date, name, and image name.
# 
# TODO: put any regex you'll be using to filter data or get image names here

# In[6]:


# PUT DEATH DATE REGEX HERE
date_re = re.compile(r'(?P<month>Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)\.? (?P<day>\d{1,2})(?:, (?P<year>\d{4}))')
# PUT NAME REGEX HERE
name_re = re.compile(r'(?P<firstNames>(?:[\'\"]?[A-Z][\'\"A-Za-z]+ )+(?:[A-Z]. )*)(?P<lastName>[A-Z][\'A-Za-z]+)')
# PUT IMAGE NAME REGEX HERE (if you're outputting the image name into the OCR)
image_re = re.compile(r'IMAGE:(?P<imageName>[^\n]+)')


# ## Define column names (will be printed at top of file)
# 
# TODO: If you want column names printed at the top, write the titles you want in order here

# In[7]:


column_names = ['Image','First_Names', 'Last_Name', 'Death_Date_Day', 'Death_Date_Month', 'Death_Date_Year', 'Names', 'Dates','Locations']


# # Run spaCy

# In[8]:


def run_spacy(text):
    
    # lists that hold the named entities in the obituary
    names = []
    dates = []
    locations = []
    
    matches = NER(text)
    
    date_count = 0
    gpe_count = 0
    
    for word in matches.ents:
        if word.label_ == 'PERSON':
            names.append(word.text)
        elif word.label_ == 'DATE':
            dates.append(word.text)
            date_count += 1
        elif word.label_ == 'GPE':
            locations.append(word.text)
            gpe_count += 1
            
    return names, dates, locations    
    


# # Processing
# 
# These run through either the name, date, or location list and return the first list entry that matches the regex (formatted). If necessary, add more functions with the variations you need to get specific data.

# ## Death date
# 
# Returns the first full date in the obituary, which is hopefully the death date
# 
# Note: uses capturing groups named 'month', 'day', and 'year'. Change if necessary.

# In[9]:


def death_date(dates):
    
    for date in dates:
        re_match = date_re.search(date)
        if re_match:
            month = month_to_int(re_match.group('month')) # convert text month to the month number
            day = int(re_match.group('day'))
            year = int(re_match.group('year'))
            return [day, month, year]
        
    return [0, 0, 0]
        


# ## Focus Person's Name
# 
# Returns the first full name in the obituary (which is hopefully a name and hopefully the person the obituary is about)
# 
# Note: uses capturing groups called 'firstNames' and 'lastName'. Change if necessary.

# In[10]:


def focus_person(names):
    
    for name in names:
        re_match = name_re.search(name)
        if re_match:
            first_names = re_match.group('firstNames')
            last_name = re_match.group('lastName') 
            return [first_names, last_name] 
    
    return ['', '']
    


# # Helper Functions

# ## Extract image name
# 
# Get the image name out of the OCR
# 
# Note: uses a named capturing group called 'imageName'. Change if necessary.

# In[11]:


def get_image_name(string):
    image = image_re.search(string)
    if image:
        return image.group('imageName')
    else:
        return ''
    
    
    


# ## Print labels
# 
# Prints out each named entity that it found along with the label it gave

# In[12]:


def print_labels(matches): # param: output from NER
    print(text)
    print('')
    for word in matches.ents:
        print(word.text, word.label_)
    print('#############################')


# ## Convert month to int

# In[13]:


def month_to_int(month):
    if month == 'Jan' or month == 'January':
        return 1
    elif month == 'Feb' or month == 'February':
        return 2
    elif month == 'Mar' or month == 'March':
        return 3
    elif month == 'Apr' or month == 'April':
        return 4
    elif month == 'May':
        return 5
    elif month == 'Jun' or month == 'June':
        return 6
    elif month == 'Jul' or month == 'July':
        return 7
    elif month == 'Aug' or month == 'August':
        return 8
    elif month == 'Sep' or month == 'Sept' or month == 'September':
        return 9
    elif month == 'Oct' or month == 'October':
        return 10
    elif month == 'Nov' or month == 'November':
        return 11
    else:
        return 12

# # File sorting helper
#
# Define an order for file names (order based on the numbers found in them)

def fileNameSort(name):
    return int(''.join(re.findall(r'\d', name)))

# # Main Code Body
# 
# Does the active stuff. If you add more functions to filter out additional information, etc., put code here to call that function and output the results in the file.

# In[14]:



os.chdir(OUTPUT_PATH)

# spacy stuff - disable makes sure it loads only the NER part
NER = spacy.load("en_core_web_sm", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])

with open(target, 'a', newline='', encoding='utf-8-sig') as fout:
    writer = csv.writer(fout)
    writer.writerow(column_names)
    
    os.chdir(INPUT_PATH)
    
    # runs through each file in the input folder
    # CHANGE STUFF HERE TO MAKE IT GO IN ORDER
    fileNames = [i for i in os.listdir() if i[-4:] == '.txt'].sort(key = fileNameSort)
    for txt in fileNames:
        os.chdir(INPUT_PATH)
    
        # Use the split_input() function to split the text document, so the OCR output for each source image is separate
        print(f'finding obituaries in {txt}...')
        split_strings = split_input(pre_process(txt))
        num = len(split_strings)
        print(f'found {num} obituaries. Writing to file {target}...')
    
        os.chdir(OUTPUT_PATH)
        
        # Run spaCy on the OCR text from each image and filter it
        for obit in split_strings:
            
            string = obit.replace('\n', ' ') # take out newlines
            string = string.replace('- ', '') # take out gaps where it was one word
            
            names = []
            dates = []
            locations = []
            
            columns = [] # list of strings that will become each entry in a row
            
            # get image name
            image_name = get_image_name(string)
            columns.append(image_name)
                
            # use NER to get lists of names and locations
            names, dates, locations = run_spacy(string)
            
            # use regex to find the focus person (first full name in the NER stuff)
            name_sections = focus_person(names)
            columns.extend(name_sections)
            
            # use regex to find death date (first full date in the NER stuff)
            date_sections = death_date(dates)
            columns.extend(date_sections)
            
            # IF YOU USE REGEX TO FILTER MORE DATA, ADD IT TO THE COLUMNS HERE
            
            # combine names, dates, and locations into one string per category and output
            names_str = ";".join(names) # makes a list into a single string
            dates_str = ";".join(dates)
            locations_str = ";".join(locations)
            columns.extend([names_str, dates_str, locations_str])
            
            # Write out the row
            writer.writerow(columns)


# In[ ]:





# In[ ]:




