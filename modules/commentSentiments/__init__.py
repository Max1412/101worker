config = {
    'wantdiff': False,
    'wantsfiles': False,
    'threadsafe': True,
    'behavior': {
        'creates': [['dump', 'programmingLanguagePerContribution']],
        'uses': [['dump', 'wiki-links']]
    }
}


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
    context.write_dump('programmingLanguagePerContribution', contributions)

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
