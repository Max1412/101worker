import sys
import json
import os

sys.path.append('..')
import interpretRules

sys.path.append('../../libraries/101meta')
import const101
import tools101

import logging

sys.path.append('../../libraries')
from service_api import *


def main(data):

    logging.basicConfig(filename='matchSimpleRules.log',level=logging.DEBUG)

    data = expand_data(data)

    rules = json.load(open(const101.rulesDump))
    rules = interpretRules.group_fast_predicates(rules)

    interpretRules.apply_rules(data['data'], rules, lambda rule: any(filter(lambda key: key  == 'fpredicate', rule['rule'].keys())), True)