config = {
    'wantdiff': False,
    'wantsfiles': False,
    'threadsafe': True,
    'behavior': {
        'creates': [['dump', 'commentSentiments']],
        'uses': [['dump', 'contributionCommentFilter']]
    }
}

import numpy as np
import matplotlib.pyplot as plt

def plotSentiments(title, with_neutral, data):
    neutrals = []
    compounds = []
    negatives = []
    positives = []
    legend = []
    for l, item_data in data.items():
        average_scores_data = item_data['averageScores']
        if average_scores_data['neu'] != average_scores_data['neg'] != average_scores_data['pos'] != average_scores_data['compound'] != 0:
            neutrals += [average_scores_data['neu']]
            compounds += [average_scores_data['compound']]
            negatives += [average_scores_data['neg']]
            positives += [average_scores_data['pos']]
            legend += [l]
    
    fig, ax = plt.subplots()
    fig.canvas.set_window_title(title)
    N = len(legend)
    offset = 0.0
    elements = 3
    if with_neutral:
        elements = 4
    width = 1.0/(1.0+elements)
    ind = np.arange(N)
    if with_neutral:
        neutral_bar = ax.bar(ind, neutrals, width, color='r')
        offset += width
    positive_bar = ax.bar(ind + offset, positives, width, color='g')
    offset += width
    negative_bar = ax.bar(ind + offset, negatives, width, color='r')
    offset += width
    compound_bar = ax.bar(ind + offset, compounds, width, color='b')
    ax.set_ylabel('Average scores')
    ax.set_title(title)
    ax.set_xticks(ind + elements/2.*width)
    ax.set_xticklabels(legend)
    if with_neutral:
        ax.legend((neutral_bar[0], positive_bar[0], negative_bar[0], compound_bar[0]), ('neutral', 'positive', 'negative', 'compound'))
    else:
        ax.legend((positive_bar[0], negative_bar[0], compound_bar[0]), ('positive', 'negative', 'compound'))
    ax.autoscale_view()
    plt.show()

def run(context):
    pages = context.read_dump('wiki-links')

    if pages is not None and "wiki" in pages.keys():
        pages = pages["wiki"]
        if pages is not None and "pages" in pages.keys():
            pages = pages["pages"]
    else:
        pages = []

# What this does: 1. Get list of all programming languages:
#                     (loop through namespace language, select those who are
# "programming" languages)
#                 2. Loop through contributions in wiki pages (see below) and
# search for "Uses::Language:<language>"

    languages = []
    for item in pages:
        if "p" in item.keys() and item["p"] == "Language":
           if "n" in item.keys() and "internal_links" in item.keys():
                title = item["n"]
                for x in item["internal_links"]:
                    if "programming language" in x:
                        languages += [title]
                        break;

    contributions = {}
    for item in pages:
        if "p" in item.keys() and item["p"] == "Contribution":
            if "n" in item.keys() and "internal_links" in item.keys():
                title = item["n"]
                contributions[title] = []
                for l in languages:
                    contributions[title] += [l] if "Uses::Language:"+l in item["internal_links"] else []

    contribution_sentiments = context.read_dump('contributionCommentFilter')
    num_sentences = {}
    scores = {}
    for c, data in contribution_sentiments.items():
        lang = contributions[c]
        for l in lang:
            if not l in num_sentences:
                num_sentences[l] = 0
            num_sentences[l] += data['sentences']
            if not l in scores:
                scores[l] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            for k in scores[l]:
                scores[l][k] += data['scores'][k]
    language_sentiments = {}
    for l in num_sentences:
        language_sentiments[l] = {}
        average_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average_scores:
            if num_sentences[l] == 0:
                average_scores[key] = 0
            else:
                average_scores[key] = scores[l][key]/num_sentences[l]
        language_sentiments[l]['averageScores'] = average_scores
    
    plotSentiments("Contribution comment sentiments", False, contribution_sentiments)
    plotSentiments("Language comment sentiments", False, language_sentiments)

import unittest
from unittest.mock import Mock, patch


class ProgrammingLanguagePerContribution(unittest.TestCase):

    def setUp(self):
        self.env = Mock()
        self.env.read_dump.return_value = {
            "wiki": {
                "pages": [
                    {
                        "p": "Language",
                         "n": "Java",
                         "internal_links": [
                             "OO programming language",
                             "Technology:Java platform",
                             "Technology:Java SE",
                             "InstanceOf::OO programming language"
                         ]
                     },
                    {
                        "p": "Contribution",
                        "n": "javaJson",
                         "internal_links": [
                             "Language:JSON",
                             "Language:Java",
                             "Technology:javax.json",
                             "API",
                             "Contribution:dom",
                             "Contribution:jdom",
                             "Language:JSON",
                             "Language:XML",
                             "Contribution:javaJsonHttp",
                             "Technology:Gradle",
                             "Technology:Eclipse",
                             "Implements::Feature:Hierarchical company",
                             "Implements::Feature:Mapping",
                             "Implements::Feature:Parsing",
                             "Implements::Feature:Total",
                             "Implements::Feature:Cut",
                             "MemberOf::Theme:Java mapping",
                             "Uses::Language:Java",
                             "Uses::Language:JSON",
                             "Uses::Technology:javax.json",
                             "Uses::Technology:JUnit",
                             "Uses::Technology:Gradle",
                             "DevelopedBy::Contributor:rlaemmel"
                         ]
                    }
                ]
            }
        }

    def test_pages(self):
        run(self.env)
        self.env.write_dump.assert_called_with('programmingLanguagePerContribution', {'javaJson': ['Java']})

    def test_empty(self):
        self.env.read_dump.return_value = {}
        run(self.env)
        self.env.write_dump.assert_called_with('programmingLanguagePerContribution', {})

def test():
    suite = unittest.TestLoader().loadTestsFromTestCase(ProgrammingLanguagePerContribution)
    unittest.TextTestRunner(verbosity=2).run(suite)
