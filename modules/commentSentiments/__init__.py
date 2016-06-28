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
from matplotlib.backends.backend_pdf import PdfPages

def plotSentiments(pp, title, with_neutral, data, total_scores):
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
        ax.axhline(total_scores['neu'], color='r', alpha=0.5)
        offset += width
    positive_bar = ax.bar(ind + offset, positives, width, color='g')
    ax.axhline(total_scores['pos'], color='g', alpha=0.5)
    offset += width
    negative_bar = ax.bar(ind + offset, negatives, width, color='r')
    ax.axhline(total_scores['neg'], color='r', alpha=0.5)
    offset += width
    compound_bar = ax.bar(ind + offset, compounds, width, color='b')
    ax.axhline(total_scores['compound'], color='b', alpha=0.5)
    ax.set_ylabel('Average scores')
    ax.set_title(title)
    ax.set_xticks(ind + elements/2.*width)
    ax.set_xticklabels(legend)
    ax.yaxis.grid(True, linestyle='--', which='major',
                   color='grey', alpha=.25)
    if with_neutral:
        fig.legend((neutral_bar[0], positive_bar[0], negative_bar[0], compound_bar[0]), ('neutral', 'positive', 'negative', 'compound'), 'upper right')
    else:
        fig.legend((positive_bar[0], negative_bar[0], compound_bar[0]), ('positive', 'negative', 'compound'), 'upper right')
    ax.autoscale_view()
    #plt.show()
    plt.savefig(pp, format='pdf')

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
    devs = {}
    for item in pages:
        if "p" in item.keys() and item["p"] == "Contribution":
            if "n" in item.keys():
                if "internal_links" in item.keys():
                    title = item["n"]
                    contributions[title] = []
                    for l in languages:
                        contributions[title] += [l] if "Uses::Language:"+l in item["internal_links"] else []
                if "DevelopedBy" in item.keys():
                    devs[title] = []
                    for dev in item["DevelopedBy"]:
                        devs[title] += [dev['n']]

    contribution_sentiments = context.read_dump('contributionCommentFilter')
    lang_num_sentences = {}
    lang_scores = {}
    dev_num_sentences = {}
    dev_scores = {}
    total_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    total_sentences = 0
    for c, data in contribution_sentiments.items():
        total_sentences += data['sentences']
        for k in total_scores:
            total_scores[k] += data['scores'][k]
        lang = contributions[c]
        for l in lang:
            if not l in lang_num_sentences:
                lang_num_sentences[l] = 0
            lang_num_sentences[l] += data['sentences']
            if not l in lang_scores:
                lang_scores[l] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            for k in lang_scores[l]:
                lang_scores[l][k] += data['scores'][k]
        dev = devs[c]
        for d in dev:
            if not d in dev_num_sentences:
                dev_num_sentences[d] = 0
            dev_num_sentences[d] += data['sentences']
            if not d in dev_scores:
                dev_scores[d] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            for k in dev_scores[d]:
                dev_scores[d][k] += data['scores'][k]
    for t in total_scores:
        if total_sentences == 0:
            total_scores[t] = 0
        else:
            total_scores[t] = total_scores[t]/total_sentences
    language_sentiments = {}
    for l in lang_num_sentences:
        language_sentiments[l] = {}
        average_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average_scores:
            if lang_num_sentences[l] == 0:
                average_scores[key] = 0
            else:
                average_scores[key] = lang_scores[l][key]/lang_num_sentences[l]
        language_sentiments[l]['averageScores'] = average_scores
    developer_sentiments = {}
    for d in dev_num_sentences:
        developer_sentiments[d] = {}
        average_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average_scores:
            if dev_num_sentences[d] == 0:
                average_scores[key] = 0
            else:
                average_scores[key] = dev_scores[d][key]/dev_num_sentences[d]
        developer_sentiments[d]['averageScores'] = average_scores

    pp = PdfPages(context.get_env('dumps101dir') + '/multipage.pdf')
    plotSentiments(pp, "Contribution comment sentiments", False, contribution_sentiments, total_scores)
    plotSentiments(pp, "Language comment sentiments", False, language_sentiments, total_scores)
    plotSentiments(pp, "Developer comment sentiments", False, developer_sentiments, total_scores)

    pp.close()

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
