#!/bin/bash

# Copyright 2020 Mani Sarkar

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from itertools import groupby

import re
# Sentiment Analysis
from textblob import TextBlob
from textblob import Word

import emoji
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

import nltk
nltk.download('stopwords')
STOP_WORDS = set(stopwords.words('english'))

nltk.download('punkt')


### Emojis

def apply_text_profiling(dataframe, text_column):
	new_dataframe = dataframe.copy()
	new_dataframe['sentiment_polarity_score'] = new_dataframe[text_column].apply(sentiment_polarity_score)
	new_dataframe['sentiment_polarity'] = new_dataframe['sentiment_polarity_score'].apply(sentiment_polarity)
	new_dataframe['sentiment_subjectivity_score'] = new_dataframe[text_column].apply(sentiment_subjectivity_score)
	new_dataframe['sentiment_subjectivity'] = new_dataframe['sentiment_subjectivity_score'].apply(sentiment_subjectivity)
	new_dataframe['spellcheck_score'] = new_dataframe[text_column].apply(spellcheck_score)
	new_dataframe['spelling_quality'] = new_dataframe['spellcheck_score'].apply(spelling_quality)
	new_dataframe['sentences_count'] = new_dataframe[text_column].apply(count_sentences)
	new_dataframe['characters_count'] = new_dataframe[text_column].apply(len)
	new_dataframe['spaces_count'] = new_dataframe[text_column].apply(count_spaces)
	new_dataframe['words_count'] = new_dataframe[text_column].apply(words_count)
	new_dataframe['duplicates_count'] = new_dataframe[text_column].apply(count_duplicates)
	new_dataframe['chars_excl_spaces_count'] = new_dataframe[text_column].apply(count_characters_excluding_spaces)
	new_dataframe['emoji_count'] = new_dataframe[text_column].apply(count_emojis)
	new_dataframe['whole_numbers_count'] = new_dataframe[text_column].apply(count_whole_numbers)
	new_dataframe['alpha_numeric_count'] = new_dataframe[text_column].apply(count_alpha_numeric)
	new_dataframe['non_alpha_numeric_count'] = new_dataframe[text_column].apply(count_non_alpha_numeric)
	new_dataframe['punctuations_count'] = new_dataframe[text_column].apply(count_punctuations)
	new_dataframe['stop_words_count'] = new_dataframe[text_column].apply(count_stop_words)
	new_dataframe['dates_count'] = new_dataframe[text_column].apply(count_dates)

	return new_dataframe

# Docs: https://textblob.readthedocs.io/en/dev/quickstart.html

def sentiment_polarity(score):
	score = float(score)
	if score < 0:
		return "Negative"
	if score > 0:
		return "Positive"
	return "Neutral"


def sentiment_polarity_score(text):
	return TextBlob(text).sentiment.polarity

 ### See https://en.wikipedia.org/wiki/Words_of_estimative_probability
 
subjectivity_words_of_probability_estimation = [
    ["Very subjective", 99, 100],  # Certain: 100%: Give or take 0%
    ### The General Area of Possibility
    ["Quite subjective", 87, 99],  # Almost Certain: 93%: Give or take 6%
    ["Pretty subjective", 63, 87],  # Probable: 75%: Give or take about 12%
    ["Objective/subjective", 40, 63],  # Chances About Even: 50%: Give or take about 10%
    ["Pretty objective", 12, 40],  # Probably Not: 30%: Give or take about 10%
    ["Quite objective", 2, 12],  # Almost Certainly Not 7%: Give or take about 5%
    ["Very objective", 0, 2]  # Impossible 0%: Give or take 0%
]

def sentiment_subjectivity(score):
	score = float(score) * 100
	for each_slab in subjectivity_words_of_probability_estimation:
		if (score >= each_slab[1]) and (score <= each_slab[2]):
			return each_slab[0]

def sentiment_subjectivity_score(text):
	return TextBlob(text).sentiment.subjectivity

spellcheck_words_of_probability_estimation = [
    ["Good", 99, 100],  # Certain: 100%: Give or take 0%
    ### The General Area of Possibility
    ["Quite good", 87, 99],  # Almost Certain: 93%: Give or take 6%
    ["Pretty good", 63, 87],  # Probable: 75%: Give or take about 12%
    ["So/so", 40, 63],  # Chances About Even: 50%: Give or take about 10%
    ["Pretty bad", 12, 40],  # Probably Not: 30%: Give or take about 10%
    ["Quite bad", 2, 12],  # Almost Certainly Not 7%: Give or take about 5%
    ["Bad", 0, 2]  # Impossible 0%: Give or take 0%
]

def spellcheck_score(text):
	tokenized_text = word_tokenize(text)
	total_score = 0.0
	for each_word in tokenized_text:
		spellchecked_word = Word(each_word).spellcheck()
		_, score = spellchecked_word[0]
		total_score += score
	return total_score / len(tokenized_text)

def spelling_quality(score):
	score = float(score) * 100
	for each_slab in spellcheck_words_of_probability_estimation:
		if (score >= each_slab[1]) and (score <= each_slab[2]):
			return each_slab[0]

def gather_emojis(text):
    emoji_expaned_text = emoji.demojize(text)
    return re.findall(r'\:(.*?)\:', emoji_expaned_text) 

def count_emojis(text):
    list_of_emojis = gather_emojis(text)
    return len(list_of_emojis)

### Numbers
def gather_whole_numbers(text):
    line = re.findall(r'[0-9]+', text)
    return line

def count_whole_numbers(text):
    list_of_numbers = gather_whole_numbers(text)
    return len(list_of_numbers)

### Alphanumeric
def gather_alpha_numeric(text):
    return re.findall('[A-Za-z0-9]', text)

def count_alpha_numeric(text):
    return len(gather_alpha_numeric(text))

### Non-alphanumeric
def gather_non_alpha_numeric(text):
    return re.findall('[^A-Za-z0-9]', text)

def count_non_alpha_numeric(text):
    return len(gather_non_alpha_numeric(text))

### Punctuations
def gather_punctuations(text):
    line = re.findall(r'[!"\$%&\'()*+,\-.\/:;=#@?\[\\\]^_`{|}~]*', text)
    string = "".join(line)
    return list(string)

def count_punctuations(text):
    return len(gather_punctuations(text))

### Stop words
def gather_stop_words(text):
    word_tokens = word_tokenize(text)
    found_stop_words = [word for word in word_tokens if word in STOP_WORDS]
    return found_stop_words

def count_stop_words(text):
    return len(gather_stop_words(text))

### Dates
def gather_dates(text, date_format='dd/mm/yyyy'):
    ddmmyyyy = r'\b(3[01]|[12][0-9]|0[1-9])/(1[0-2]|0[1-9])/([0-9]{4})\b'
    mmddyyyy = r'\b(1[0-2]|0[1-9])/(3[01]|[12][0-9]|0[1-9])/([0-9]{4})\b'
    regex_list =  {
        'dd/mm/yyyy': ddmmyyyy, 'mm/dd/yyyy': mmddyyyy
    }
    return re.findall(regex_list[date_format], text)

def count_dates(text):
    return len(gather_dates(text))

### Words count
def gather_words(text):
    return re.findall(r'\b[^\d\W]+\b', text)

def words_count(text):
    return len(gather_words(text))


### Sentences
def gather_sentences(text):
    lines = re.findall(r'([^.]*[^.]*)', text)
    for index, each in enumerate(lines):
        if each == '':
            del lines[index]

    return lines

### Number of spaces
def count_spaces(text):
    spaces = re.findall(r' ', text)
    return len(spaces)

### Number of characters without spaces
def gather_duplicates(text):
    tokenized_text = word_tokenize(text.lower())
    sorted_tokenized_text = sorted(tokenized_text)
    duplicates = {}
    for value, group in groupby(sorted_tokenized_text):
        frequency = len(list(group))
        if frequency > 1:
            duplicates.update({value: frequency})
                          
    return duplicates

### Duplicates
def count_duplicates(text):
    return len(gather_duplicates(text))

def count_characters_excluding_spaces(text):
    return len(text) - count_spaces(text)

def count_sentences(text):
    return len(gather_sentences(text))
