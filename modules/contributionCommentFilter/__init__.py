config = {
    'wantdiff': False,
    'wantsfiles': True,
    'threadsafe': True,
    'behavior': {
        'creates': [['dump', 'contributionCommentSentiments']],
        'uses': [['resource', 'lang']]
    }
    }

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import nltk
import os
import re

''' Comment helper functions '''

def singleline_comment_length(lang):
    if lang in ["Python", "Perl", "Ruby"]:
        return 1
    return 2

def multiline_comment_start_length(lang):
    if lang == "Python":
        return 3
    if lang == "HTML":
        return 4
    if lang == "Ruby":
        return 6
    return 2

def multiline_comment_end_length(lang):
    if lang == "Python":
        return 3
    if lang == "HTML":
        return 3
    if lang == "Ruby":
        return 4
    return 2

def is_comment_start_candidate(comment, lang):
    if comment == "/" and lang in ["Java", "CPlusPlus", "CSS", "PHP", "Scala", "JavaScript", "CSharp"]:
        return True
    if comment == "{" and lang == "Haskell":
        return True
    return False

def is_comment_end_candidate(comment, lang):
    if comment == "*" and lang in ["Java", "CPlusPlus", "CSS", "PHP", "Scala", "JavaScript", "CSharp"]:
        return True
    if comment == "-" and lang == "Haskell":
        return True
    return False

def is_comment_start(comment, lang):
    if comment == "#" and lang in ["Python", "PHP", "Perl", "Ruby"]:
        return True, 1
    if comment == "//" and lang in ["Java", "CPlusPlus", "PHP", "Scala", "JavaScript", "CSharp"]:
        return True, 2
    if comment == "--" and lang == "Haskell":
        return True, 2
    return False, 0

def is_multiline_comment_start(comment, lang):
    if comment == "/*" and lang in ["Java", "CPlusPlus", "CSS", "PHP", "Scala", "JavaScript", "CSharp"]:
        return True, 2
    if comment == "{-" and lang == "Haskell":
        return True, 2
    return False, 0

def is_multiline_comment_end(comment, lang):
    if comment == "-}" and lang == "Haskell":
      return True, 2
    if comment == "*/" and lang in ["Java", "CPlusPlus", "CSS", "PHP", "Scala", "JavaScript", "CSharp"]:
        return True, 2
    return False, 0

def eol(text):
    return "\n" in text

def find_comments(text, lang):
    ''' Extract comments from source string according to the language specified. '''
    text = list(text) # Convert text to list to ensure iterablility
    comments = []
    # Save current type of comment
    oneline_comment = False
    multiline_comment = False
    start = 0
    line = 0
    current_oneline_comment_line = 0 # Used if joining multiple consecutive single line comments is necessary.
    is_currently_string = 0
    for i, c in enumerate(text):
        if eol(''.join(text[i:i+1])):
            line += 1
        if oneline_comment:
            # If the current comment is a single line comment, end it at the end of the line
            if eol(''.join(text[i:i+1])):
                comments += [''.join(text[start:i+1])] # save comment from comment start to eol
                # if the previous line was a single line comment too, join both comments
                if current_oneline_comment_line + 1 == line:
                    comments[-2:] = [''.join(comments[-2:])]
                current_oneline_comment_line = line
                oneline_comment = False # Comment is now over
            continue
        if multiline_comment:
            if is_comment_end_candidate(c, lang):
                # if the current character is an multiline end candiate,
                # check if this and the next x chars necessary to end the
                # multiline comment in the current language, match the
                # characters that end the comment
                is_end, c_length = is_multiline_comment_end(''.join(text[i:i + multiline_comment_end_length(lang)]), lang)
                if is_end:
                    # if they match the end comment, add the lines to the
                    # comments list
                    comments += [''.join(text[start:i+1-c_length])]
                    multiline_comment = False
            continue
        # Skip strings so comment characters are not recognized while in strings.
        # This code is not reached if there currently is a comment, so quotes
        # comments still work.
        if c == '"' or c == "'":
            is_currently_string += 1
        if is_currently_string % 2 == 1:
            continue
        # Check if the string starting at the current char with the length of
        # the singleline comment acutally is a comment string.
        # If this is the case, set comment start to the char after the comment characters.
        is_c_start, c_length = is_comment_start(''.join(text[i:i + singleline_comment_length(lang)]), lang)
        if is_c_start:
            start = i+c_length
            oneline_comment = True
        elif is_comment_start_candidate(c, lang):
            # If there is no single line comment, check for multiline comments.
            # This behavior corresponds to the way, single line comment checking works.
            is_m_c_start, c_length = is_multiline_comment_start(''.join(text[i:i + multiline_comment_start_length(lang)]), lang)
            if is_m_c_start:
                start = i+c_length
                multiline_comment = True
    return comments

def find_special_multiline_comments(source, lang):
    ''' Look for multiline comments that follow special rules and could not
    be included in the find_comments method because of their complexity.
    Comments from the find_comments method are not recognized and both functions work in conjunction.'''
    comments = []
    multiline_comment = False
    comment_start = ""
    comment_end = ""
    if lang == "Python":
        comment_start = ['"""', '\'\'\'']
        comment_end = ['"""', '\'\'\'']
    elif lang == "Ruby":
        comment_start = ['=begin']
        comment_end = ['=end']
    elif lang == "HTML":
        comment_start = ['<!--']
        comment_end = ['-->']
    else:
        return []
    start = 0 # comment start line
    end = 0 # comment end line
    lines = source.split("\n")
    i = 0 # line counter
    for line in lines:
        line = line.strip()
        # This is for single line doctype style comments, mainly used in Python.
        # Only lines with actual comment are considered.
        # Check if start of line is an actual comment start,
        # same for the end of the line.
        if len(line) >= multiline_comment_start_length(lang) + multiline_comment_end_length(lang) and line[:multiline_comment_start_length(lang)] in comment_start and line[-multiline_comment_end_length(lang):] in comment_end:
            # Don't end comment if the opening comment chars are different from
            # the closing characters. This is a python only issue.
            if lang == "Python" and line[:multiline_comment_start_length(lang)] != line[-multiline_comment_end_length(lang):]:
                start = i
                continue
            # Strip comment characters from the comment content
            comments += [line[multiline_comment_start_length(lang):-multiline_comment_end_length(lang)]]
            continue
        # Check if the current line ends the multiline comment and if there
        # actually is a comment that can end.
        if line[-multiline_comment_end_length(lang):] in comment_end and multiline_comment:
            end = i+1
            comment = ''.join(lines[start:end]) # create comment by joining all lines from start to end
            comment = comment.strip() # remove whitespace
            # Check if end and start of comment are equal since Python has 2
            # types of multiline comment types, which are independent.
            if lang == "Python" and comments[:multiline_comment_start_length(lang)] != comments[-multiline_comment_end_length(lang):]:
                # Skip the current line
                continue
            # Strip comment characters from the comment content
            comments += [comment[multiline_comment_start_length(lang):-multiline_comment_end_length(lang)]]
            multiline_comment = False # end multiline comment
        # Check if current line starts the multi line comment
        if line[:multiline_comment_start_length(lang)] in comment_start:
            multiline_comment = True
            start = i
        i += 1
    return comments

def strip_comments(comments):
    '''Split comments into sentences. Remove leading and trailing whitespace
    from multiline comments, as well as leading special characters such as * in
    several Java comment styles.'''
    final_comments = []
    for comment in comments:
        fixed_comment = ""
        for line in comment.split('\n'):
            line = line.strip()
            m = re.search("[a-zA-Z0-9]", line)
            if m is None:
                continue
            line = line[m.start():]
            line = line.strip()
            fixed_comment += " " + line
        fixed_comment = tokenize.sent_tokenize(fixed_comment.strip())
        final_comments += fixed_comment
    return final_comments

'''
Extracts comments from a file written in a few languages including Java, Python, Haskell. These comments are then split into sentences excluding those with 3 or less words, to exclude low effort comments from the calculation.
Analyze the sentences using nltk's vader sentiment analyzer to produce a outcome in the following form:
    {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
Save a multitude of data including:
  * average sentiments (with and without neutral sentences)
  * accumulated sentiments (with and without neutral sentences)
  * number of sentences (with and without neutral sentences)
  * number of skipped sentences due to insufficient length
This data is categorized by contribution to ensure further processing is possible.
'''

def run(context, res):

    # download nltk lists (if not already downloaded)
    # nltk.download('punkt')
    # nltk.download('vader_lexicon')

    data = context.read_dump('contributionCommentFilter')

    if data is None:
        data = {}
    f = res['file']
    if f.startswith('contributions' + os.sep):
        contribution = f.split(os.sep)[1]
    # These are accumulated values to ensure correct averages
    num_sentences = 0
    num_too_short_sentences = 0
    num_without_neutral = 0
    scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    scores_without_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    # Check if there is actual data in the dump, and if there is, assign these
    # values to the corresponding variables in this program.
    if data.get(contribution, None) is None:
        data[contribution] = {}
    if data[contribution].get("sentences", None) is not None:
        num_sentences = data[contribution]["sentences"]
    if data[contribution].get("shortSentences", None) is not None:
        num_too_short_sentences = data[contribution]["shortSentences"]
    if data[contribution].get("nonNeutralSentences", None) is not None:
        num_without_neutral = data[contribution]["nonNeutralSentences"]
    if data[contribution].get("scores", None) is not None:
        scores = data[contribution]["scores"]
    if data[contribution].get("nonNeutralScores", None) is not None:
        scores_without_neutral = data[contribution]["nonNeutralScores"]

    try: # Use a try catch block in case of unicode errors
        source = context.get_primary_resource(f)
        lang = context.get_derived_resource(f, "lang")
        comments = []
        comments += find_comments(source, lang)
        comments += find_special_multiline_comments(source, lang)
        sentences = strip_comments(comments)

        sid = SentimentIntensityAnalyzer() # Initialize nltk vader sentiment analyzer
        for sentence in sentences:
            # skip sentences with insufficient length
            if len(sentence.split()) > 3:
                # skip sentences starting with the author tag
                if not sentence.startswith("author"):
                    num_sentences += 1
                    ss = sid.polarity_scores(sentence) # use vader to calculate scores
                    if ss["neu"] < 1:
                        # Add scores that are not exclusively neutral to the
                        # non-neutral score accumulator.
                        num_without_neutral += 1
                        for k in sorted(ss):
                            scores_without_neutral[k] += ss[k]
                    for k in sorted(ss):
                        scores[k] += ss[k] # add scores to accumulated scores
            else:
                num_too_short_sentences += 1;

        average = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        average_without_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        # Calculate averages from current value of accumulated scores
        # and sentence numbers.
        for key in average:
            if num_sentences == 0:
                average[key] = 0
            else:
                average[key] = scores[key]/num_sentences
            if num_without_neutral == 0:
                average_without_neutral[key] = 0
            else:
                average_without_neutral[key] = scores_without_neutral[key] / num_without_neutral

        # Create data dictionary and save to dump
        data[contribution] = {"scores": scores, "nonNeutralScores": scores_without_neutral, "sentences": num_sentences, "nonNeutralSentences": num_without_neutral, "tooShortSentences": num_too_short_sentences, "averageScores": average, "averageNonNeutral": average_without_neutral}

        context.write_dump('contributionCommentSentiments', data)
    except UnicodeEncodeError:
        print("UnicodeEncodeError")

import unittest
from unittest.mock import Mock


class ContributionCommentFilter(unittest.TestCase):

    def setUp(self):
        self.env=Mock()

    def test_run(self):
        res = {
            'file': 'contributions' + os.sep + 'python' + os.sep + 'test.py'
        }
        primaryResource = """#just a prank
        #bro.
        if hello == True:
        #love.
        '''the quick brown frog jumps over the lazy dog. i love christmas alot.'''
        """
        self.env.read_dump.return_value = {}
        self.env.get_derived_resource.return_value = "Python"
        self.env.get_primary_resource.return_value = primaryResource
        run(self.env, res)
        self.env.write_dump.assert_called_with('contributionCommentSentiments',   {'python': {'averageScores': {'neg': 0.07933333333333333, 'pos': 0.22566666666666668, 'neu': 0.695, 'compound': 0.0919}, 'nonNeutralSentences': 2, 'sentences': 3, 'scores': {'neg': 0.238, 'pos': 0.677, 'neu': 2.085, 'compound': 0.2757}, 'averageNonNeutral': {'neg': 0.119, 'pos': 0.3385, 'neu': 0.5425, 'compound': 0.13785}, 'tooShortSentences': 1, 'nonNeutralScores': {'neg': 0.238, 'pos': 0.677, 'neu': 1.085, 'compound': 0.2757}}})

    def test_too_short_sentences(self):
        res = {
            'file': 'contributions' + os.sep + 'python' + os.sep + 'test.py'
        }
        primaryResource = """# not recognized
        if hello == True:
        # this is short.
        '''A comment. Multiline.'''
        """
        self.env.read_dump.return_value = {}
        self.env.get_derived_resource.return_value = "Python"
        self.env.get_primary_resource.return_value = primaryResource
        run(self.env, res)
        self.env.write_dump.assert_called_with('contributionCommentSentiments',   {'python': {'averageScores': {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}, 'nonNeutralSentences': 0, 'sentences': 0, 'scores': {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}, 'averageNonNeutral': {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}, 'tooShortSentences': 4, 'nonNeutralScores': {'neg': 0, 'pos': 0, 'neu': 0, 'compound': 0}}})



def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(ContributionCommentFilter)
    unittest.TextTestRunner(verbosity=2).run(suite)
