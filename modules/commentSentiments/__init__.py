config = {
    'wantdiff': False,
    'wantsfiles': False,
    'threadsafe': True,
    'behavior': {
        'creates': [['dump', 'languageCommentSentiments'],
        ['dump', 'developerCommentSentiments']],
        'uses': [['dump', 'contributionCommentSentiments']]
    }
}

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def plotSentiments(pp, title, ylabel, with_neutral, data, total_scores, use_non_neutral_scores=False):
    neutrals = []
    compounds = []
    negatives = []
    positives = []
    legend = []
    for l, item_data in data.items():
        average_scores_data = item_data['averageScores']
        if use_non_neutral_scores:
            average_scores_data = item_data['averageNonNeutral']
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
        neutral_bar = ax.bar(ind, neutrals, width, color='y')
        ax.axhline(total_scores['neu'], color='y', alpha=0.5)
        offset += width
    positive_bar = ax.bar(ind + offset, positives, width, color='g')
    ax.axhline(total_scores['pos'], color='g', alpha=0.5)
    offset += width
    negative_bar = ax.bar(ind + offset, negatives, width, color='r')
    ax.axhline(total_scores['neg'], color='r', alpha=0.5)
    offset += width
    compound_bar = ax.bar(ind + offset, compounds, width, color='b')
    ax.axhline(total_scores['compound'], color='b', alpha=0.5)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ind + elements/2.*width)
    lsize = 1.0/N * 10.0 + 5.0
    ax.set_xticklabels(legend, fontsize=lsize)
    ax.yaxis.grid(True, linestyle='--', which='major',
                   color='grey', alpha=.25)
    if with_neutral:
        fig.legend((neutral_bar[0], positive_bar[0], negative_bar[0], compound_bar[0]), ('neutral', 'positive', 'negative', 'compound'), 'upper right')
    else:
        fig.legend((positive_bar[0], negative_bar[0], compound_bar[0]), ('positive', 'negative', 'compound'), 'upper right')
    ax.autoscale_view()
    plt.savefig(pp, format='pdf')


def run(context):
    pages = context.read_dump('wiki-links')

    if pages is not None and "wiki" in pages.keys():
        pages = pages["wiki"]
        if pages is not None and "pages" in pages.keys():
            pages = pages["pages"]
    else:
        pages = []

    # Only consider languages for language classification that are programming languages
    programming_languages = []
    for item in pages:
        if "p" in item.keys() and item["p"] == "Language":
           if "n" in item.keys() and "internal_links" in item.keys():
                title = item["n"]
                for x in item["internal_links"]:
                    if "programming language" in x:
                        programming_languages += [title]
                        break;

    # Extract languages and developers per contribution from wiki-links dump
    languages = {}
    devs = {}
    for item in pages:
        if "p" in item.keys() and item["p"] == "Contribution":
            if "n" in item.keys():
                if "internal_links" in item.keys():
                    title = item["n"]
                    languages[title] = []
                    for l in programming_languages:
                        languages[title] += [l] if "Uses::Language:"+l in item["internal_links"] else []
                if "DevelopedBy" in item.keys():
                    devs[title] = []
                    for dev in item["DevelopedBy"]:
                        devs[title] += [dev['n']]

    contribution_sentiments = context.read_dump('contributionCommentSentiments')

    # total scores are used to create an overall average displayed in the bar
    # chart plotted to simplify grading of displayed data in realtion to overall
    # data in the chart.
    total_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    total_non_neutral_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
    total_sentences = 0
    total_non_neutral_sentences = 0
    # Create data corresponding to contribution_sentiments but classified by
    # programming language and by developer of the contribution.
    language_sentiments = {}
    developer_sentiments = {}
    for c, data in contribution_sentiments.items():
        total_sentences += data['sentences']
        total_non_neutral_sentences += data['nonNeutralSentences']
        for k in total_scores:
            total_scores[k] += data['scores'][k]
            total_non_neutral_scores[k] += data['nonNeutralScores'][k]
        lang = languages[c]
        for l in lang:
            if l not in language_sentiments:
                language_sentiments[l] = {}
                language_sentiments[l]['sentences'] = 0
                language_sentiments[l]['tooShortSentences'] = 0
                language_sentiments[l]['nonNeutralSentences'] = 0
                language_sentiments[l]['scores'] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
                language_sentiments[l]['nonNeutralScores'] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            language_sentiments[l]['sentences'] += data['sentences']
            language_sentiments[l]['tooShortSentences'] += data['tooShortSentences']
            language_sentiments[l]['nonNeutralSentences'] += data['nonNeutralSentences']
            for k in language_sentiments[l]['scores']:
                language_sentiments[l]['scores'][k] += data['scores'][k]
                language_sentiments[l]['nonNeutralScores'][k] += data['nonNeutralScores'][k]
        dev = devs[c]
        for l in dev:
            if l not in developer_sentiments:
                developer_sentiments[l] = {}
                developer_sentiments[l]['sentences'] = 0
                developer_sentiments[l]['tooShortSentences'] = 0
                developer_sentiments[l]['nonNeutralSentences'] = 0
                developer_sentiments[l]['scores'] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
                developer_sentiments[l]['nonNeutralScores'] = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            developer_sentiments[l]['sentences'] += data['sentences']
            developer_sentiments[l]['tooShortSentences'] += data['tooShortSentences']
            developer_sentiments[l]['nonNeutralSentences'] += data['nonNeutralSentences']
            for k in developer_sentiments[l]['scores']:
                developer_sentiments[l]['scores'][k] += data['scores'][k]
                developer_sentiments[l]['nonNeutralScores'][k] += data['nonNeutralScores'][k]
    for t in total_scores:
        if total_sentences == 0:
            total_scores[t] = 0
        else:
            total_scores[t] = total_scores[t]/total_sentences
        if total_non_neutral_sentences == 0:
            total_non_neutral_scores[t] = 0
        else:
            total_non_neutral_scores[t] = total_non_neutral_scores[t]/total_non_neutral_sentences

    for l in language_sentiments:
        average_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        average_non_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average_scores:
            if language_sentiments[l]['sentences'] == 0:
                average_scores[key] = 0
                average_non_neutral[key] = 0
            else:
                average_scores[key] = language_sentiments[l]['scores'][key]/language_sentiments[l]['sentences']
                average_non_neutral[key] = language_sentiments[l]['nonNeutralScores'][key]/language_sentiments[l]['nonNeutralSentences']
        language_sentiments[l]['averageScores'] = average_scores
        language_sentiments[l]['averageNonNeutral'] = average_non_neutral

    for l in developer_sentiments:
        average_scores = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        average_non_neutral = {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
        for key in average_scores:
            if developer_sentiments[l]['sentences'] == 0:
                average_scores[key] = 0
                average_non_neutral[key] = 0
            else:
                average_scores[key] = developer_sentiments[l]['scores'][key]/developer_sentiments[l]['sentences']
                average_non_neutral[key] = developer_sentiments[l]['nonNeutralScores'][key]/developer_sentiments[l]['nonNeutralSentences']
        developer_sentiments[l]['averageScores'] = average_scores
        developer_sentiments[l]['averageNonNeutral'] = average_non_neutral

    pp = PdfPages(context.get_env('dumps101dir') + '/commentSentiments.pdf')
    plotSentiments(pp, "Contribution comment sentiments", "Average Scores", False, contribution_sentiments, total_scores)
    plotSentiments(pp, "Non neutral contribution comment sentiments", "Average Scores", True, contribution_sentiments, total_non_neutral_scores, True)
    plotSentiments(pp, "Language comment sentiments", "Average Scores", False, language_sentiments, total_scores)
    plotSentiments(pp, "Non neutral language comment sentiments", "Average Scores", True, language_sentiments, total_non_neutral_scores, True)
    plotSentiments(pp, "Developer comment sentiments", "Average Scores", False, developer_sentiments, total_scores)
    plotSentiments(pp, "Non neutral developer comment sentiments", "Average Scores", True, developer_sentiments, total_non_neutral_scores, True)

    pp.close()

    context.write_dump('developerCommentSentiments', developer_sentiments)
    context.write_dump('languageCommentSentiments', language_sentiments)

import unittest
from unittest.mock import Mock, patch


class CommentSentiments(unittest.TestCase):

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
    suite = unittest.TestLoader().loadTestsFromTestCase(CommentSentiments)
    unittest.TextTestRunner(verbosity=2).run(suite)
