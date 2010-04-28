import logging
import sys
import csv

import nltk
from sqlalchemy import and_, desc, func, or_, select

from silcc.model import Place
from silcc.model.meta import Session
from silcc.lib.util import CIList
from silcc.lib.basictokenizer import BasicTokenizer

log = logging.getLogger(__name__)

# nltk POS codes:
# NN - noun
# NNP - proper noun
# NNS - plural noun
# VBD - verb 

pos_include = ('NN', 'NNP', 'NNS')

# These should never be tags...
reader = csv.reader(open('data/stopwords.csv'))
stop_words = CIList()
for line in reader:
    stop_words += line

def capitilization_type(text):
    '''
    Determines the type of capitilzation used:
    NORMAL - Mixture of upper and lower
    ALLCAPS - All words capitilized
    LOWER - All words lower cased
    '''
    tokens = text.split()
    capitilized = [t for t in tokens if t[0].upper() == t[0]]
    log.info('Capitilized tokens: %s', str(capitilized))
    if len(capitilized) == 0:
        return 'LOWER'
    elif len(capitilized) == len(tokens):
        return 'ALLCAPS'
    else:
        return 'NORMAL'
                 
class BasicTagger(object):

    @classmethod
    def tag(cls, text):

        if not text:
            return []

        text = text.replace("'", "")
        cap_type = capitilization_type(text)

        bt = BasicTokenizer()
        tokens = bt.tokenize(text)
        pos = nltk.pos_tag(tokens)
        log.info('POS before lower casing:%s', str(pos))

        if cap_type == 'ALLCAPS':
            # If the headline is in AllCAPS then the POS tagger
            # produces too many proper nouns, hence we de-capitilize text first
            tokens = bt.tokenize(text.lower())
            pos = nltk.pos_tag(tokens)
            log.info('POS after lower casing:%s', str(pos))

        # Only return those tokens whose pos is in the include list
        tags = [t[0] for t in pos if t[1] in pos_include and not t[0] in stop_words]

        # We want to preserve the order of tags purely for esthetic value
        # hence we will not use set()
        # We will also preserve uppercased tags if they are the first occurence

        tags_ = CIList()
        for t in tags:
            if t in tags_: continue
            if len(t) < 2: continue
            tags_.append(t)

        return tags_
        
if __name__ == '__main__':
    text = sys.argv[1]
    tags = BasicTagger.tag(text)
    print tags
