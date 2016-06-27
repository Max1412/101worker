config = {
    'wantdiff': False,
    'wantsfiles': True,
    'threadsafe': True,
    'behavior': {
        'creates': [['dump', 'contributionCommentFilter']],
        'uses': [['resource', 'lang']]
    }
    }

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import tokenize
import nltk
import os
import re

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
    text = list(text)
    comments = []
    start = 0
    oneline_comment = False
    multiline_comment = False
    line = 0
    current_oneline_comment_line = 0
    is_currently_string = 0
    for i, c in enumerate(text):
        if oneline_comment:
            if eol(''.join(text[i:i+1])):
                comments += [''.join(text[start:i+1])]
                if current_oneline_comment_line + 1 == line:
                    comments[-2:] = [''.join(comments[-2:])]
                current_oneline_comment_line = line
                oneline_comment = False
            continue
        if eol(''.join(text[i:i+1])):
            line += 1
        if multiline_comment:
            if is_comment_end_candidate(c, lang):
                is_end, c_length = is_multiline_comment_end(''.join(text[i:i + multiline_comment_end_length(lang)]), lang)
                if is_end:
                    comments += [''.join(text[start:i+1-c_length])]
                    multiline_comment = False
            continue
        if c == '"' or c == "'":
            is_currently_string += 1
        if is_currently_string % 2 == 1:
            continue
        is_c_start, c_length = is_comment_start(''.join(text[i:i + singleline_comment_length(lang)]), lang)
        if is_c_start:
            start = i+c_length
            oneline_comment = True
        elif is_comment_start_candidate(c, lang):
            is_m_c_start, c_length = is_multiline_comment_start(''.join(text[i:i + multiline_comment_start_length(lang)]), lang)
            if is_m_c_start:
                start = i+c_length
                multiline_comment = True
    return comments

def find_special_multiline_comments(source, lang):
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
    start = 0
    end = 0
    lines = source.split("\n")
    i = 0
    for line in lines:
        line = line.strip()
        if len(line) >= multiline_comment_start_length(lang) + multiline_comment_end_length(lang) and line[:multiline_comment_start_length(lang)] in comment_start and line[-multiline_comment_end_length(lang):] in comment_end:
            comments += [line[multiline_comment_start_length(lang):-multiline_comment_end_length(lang)]]
            continue
        if line[-multiline_comment_end_length(lang):] in comment_end and multiline_comment:
            multiline_comment = False
            end = i+1
            comment = ''.join(lines[start:end])
            comment = comment.strip()
            comments += [comment[multiline_comment_start_length(lang):-multiline_comment_end_length(lang)]]
        if line[:multiline_comment_start_length(lang)] in comment_start:
            multiline_comment = True
            start = i
        i += 1
    return comments

def strip_comments(comments):
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
    num_sentences = 0
    num_too_short_sentences = 0
    num_without_neutral = 0
    scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    scores_without_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    if data.get(contribution, None) is None:
        data[contribution] = {}
    else:
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

    try:
        source = context.get_primary_resource(f)
        lang = context.get_derived_resource(f, "lang")
        comments = []
        comments += find_comments(source, lang)
        source = context.get_primary_resource(f)
        comments += find_special_multiline_comments(source, lang)
        sentences = strip_comments(comments)

        sid = SentimentIntensityAnalyzer()
        for sentence in sentences:
            if len(sentence.split()) > 3:
                if not sentence.startswith("author"):
                    num_sentences += 1
                    ss = sid.polarity_scores(sentence)
                    if ss["neu"] < 1:
                        num_without_neutral += 1
                        for k in sorted(ss):
                            scores_without_neutral[k] += ss[k]
                    for k in sorted(ss):
                        scores[k] += ss[k] # add scores to total scores
            else:
                num_too_short_sentences += 1;

        # average of scores: (it is possible to do this directly, but do we need the un-averaged scores?)
        average = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        average_without_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average:
            if num_sentences == 0:
                average[key] = 0
            else:
                average[key] = scores[key]/num_sentences
            if num_without_neutral == 0:
                average_without_neutral[key] = 0
            else:
                average_without_neutral[key] = scores_without_neutral[key] / num_without_neutral   
        data[contribution] = {"scores": scores, "nonNeutralScores": scores_without_neutral, "sentences": num_sentences, "nonNeutralSentences": num_without_neutral, "tooShortSentences": num_too_short_sentences, "averageScores": average, "averageNonNeutral": average_without_neutral}

        context.write_dump('contributionCommentFilter', data)
    except UnicodeEncodeError:
        print("UnicodeEncodeError")

import unittest
from unittest.mock import Mock


class ContributionCommentFilter(unittest.TestCase):

    def setUp(self):
        self.env=Mock()

def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(CommentSentiment)
    unittest.TextTestRunner(verbosity=2).run(suite)
