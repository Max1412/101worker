config = {
    'wantdiff': False,
    'wantsfiles': False,
    'threadsafe': True,
    }

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import nltk

def run(context):

    # download nltk lists (if not already downloaded)
    nltk.download('punkt')
    nltk.download('vader_lexicon')

    sentences = [
                    "This is a negative sentence.",
                    "This is a positive sentence."
                ]

    # this is how to split texts into sentences:
    paragraph = "First sentence is good. Second sentence is bad."
    lines = tokenize.sent_tokenize(paragraph)
    sentences.extend(lines)

    scores = {
                "compound": 0,
                "pos": 0,
                "neu": 0,
                "neg": 0
              }

    num_sentences = len(sentences)

    sid = SentimentIntensityAnalyzer()

    for sentence in sentences:
        print("\n"  + sentence)
        ss = sid.polarity_scores(sentence)
        for k in sorted(ss):
            print('{0}: {1}, '.format(k, ss[k]), end='')
            scores[k] += ss[k] # add scores to total scores
    print()

    # average of scores: (it is possible to do this directly, but do we need the un-averaged scores?)
    for key in scores:
       scores[key] /= num_sentences


    print(scores)

import unittest
from unittest.mock import Mock


class CommentSentiment(unittest.TestCase):

    def setUp(self):
        self.env=Mock()





def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(CommentSentiment)
    unittest.TextTestRunner(verbosity=2).run(suite)