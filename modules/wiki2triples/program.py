#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Martin Leinberger'



import os
import sys
import json
import rdflib
from rdflib import URIRef
from rdfalchemy.sparql.sesame2 import SesameGraph
import urllib
import sesame
sys.path.append('../../libraries')
sys.path.append('../../libraries/101meta')

from metamodel import Dumps

# Setting up namespaces
ontology = rdflib.Namespace('http://101companies.org/ontology#')
resources = rdflib.Namespace('http://101companies.org/resources#')
rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
rdfs = rdflib.Namespace('http://www.w3.org/2000/01/rdf-schema#')

namespace_cache = {}
classes_in_wiki = []
debug = []


def get_namespace(namespace_name):
    if not namespace_name in namespace_cache:
        namespace_cache[namespace_name] = rdflib.Namespace('http://101companies.org/resources/'+namespace_name.strip()+'#')
    return namespace_cache[namespace_name]


# Keys to be ignored for general mapping - they might however be processed in a more specific part of the code
ignored_keys_in_contributions = ['p', 'n', 'instanceOf', 'internal_links', 'headline', 'identifies', 'subresources',
                                 'similarTo', 'linksTo', 'sameAs', 'relatesTo']
ignored_keys_in_subresources = ['internal_links']
ignored_keys_general = ['p', 'n', 'instanceOf', 'headline', 'internal_links', 'linksTo', 'isA', 'identifies',
                        'subresources', 'similarTo', 'sameAs', 'relatesTo']
ignored_keys_for_validation  = ['p', 'n', 'headline', 'internal_links', 'subresources', 'isA']

allowed_relations = {}
erroneous_pages = []


ignored_keys_validation = ['p', 'n', 'headline', 'internal_links', 'subresources', 'isA']
ignored_keys_in_instances = ['p', 'n', 'instanceOf', 'isA', 'headline', 'internal_links', 'subresources']

models = filter(lambda x: '.json' in x, os.listdir('./../validate/models'))
for model in models:
    model_name = model.replace('.json', '')
    allowed_relations[model_name] = []
    x = json.load(open('../validate/models/' + model, 'r'))
    for property in x.get('properties', []):
        allowed_relations[model_name].append(property['property'])
print allowed_relations
for y in filter(lambda x: x not in ['entity'], allowed_relations.keys()):
    allowed_relations[y] += allowed_relations['entity']


def filter_pages(wiki):
    collection = []
    namespace_blacklist = json.load(open('namespaces_blacklist.json', 'r'))
    for page in wiki:
        if not page['p'] in namespace_blacklist and page['p'].lower() in allowed_relations: #and not (page['p'] + ":" + page['n'].replace(' ', '_')) in blacklist:
            collection.append(page)
    return collection


def encode(s):
    return urllib.quote(s.replace(unichr(252), 'ue').replace(unichr(228), 'ae').replace(unichr(246), 'oe')
                        .replace(unichr(232), 'e').replace(unichr(233), 'e').replace(unichr(234), 'e')
                        .replace(unichr(244), 'o').replace(unichr(249), 'u').replace(unichr(251), 'u')
                        .replace(unichr(252), 'o').replace(unichr(225), 'a').replace(unichr(237), 'i')
                        .replace(unichr(241), 'n').replace(unichr(243), 'o').replace(unichr(250), 'u')
                        .replace(unichr(252), 'u').replace(' ', '_'))

def encode_predicate(p):
    return encode_ontology(p[0].lower() + p[1:])

def encode_ontology(s):
    return ontology[ encode(s) ]


def encode_resource(namespace, s):
    if not namespace: namespace = 'Concept'
    return get_namespace(namespace)[ encode(s) ]


def disambiguate(p):
    if 'http://' in p:
        try:
            return URIRef(urllib.quote(encode(p)))
        except:
            return URIRef('http://failedConversion.com')
        
    if ':' in p:
        namespace, name = p.split(':')[0], p.split(':')[1]
    else:
        namespace, name = 'Concept', p
    if name in classes_in_wiki or (namespace+':'+name) in classes_in_wiki:
        return resources[encode(name)]
    else:
        return encode_resource(namespace, name)


def make_ontology_classes(graph):
    # Add highest level classes
    wikipage = encode_ontology('WikiPage')
    graph.add( (wikipage, rdf['type'], rdfs['Class']) )

    entity = encode_ontology('Entity')
    entityPage = encode_ontology('EntityPage')

    graph.add( (entity, rdf['type'], rdfs['Class']) )
    graph.add( (entityPage, rdf['type'], rdfs['Class']) )
    graph.add( (entityPage, rdfs['subClassOf'], wikipage))

    for ns in ['Concept', 'Contribution', 'Technology', 'Language', 'Feature', 'Script', 'Course']:
        thing = encode_ontology(ns)
        page = encode_ontology(ns+'Page')

        graph.add( (thing, rdf['type'], rdfs['Class']) )
        graph.add( (thing, rdfs['subClassOf'], entity))

        graph.add( (page, rdf['type'], rdfs['Class']) )
        graph.add( (page, rdfs['subClassOf'], wikipage))


def hardcoded_classes(graph):
    # Adding most basic classes
    entity = encode_ontology('Entity')
    wikipage = encode_ontology('WikiPage')
    classifier = encode_ontology('Classifier')

    for s in [entity, wikipage, classifier]:
        triple = (s, rdf['type'], rdfs['Class'])
        graph.add(triple)

    # Adding instruments
    instrument = encode_ontology('Instrument')
    graph.add((instrument, rdf['type'], rdfs['Class']))
    graph.add((instrument, rdfs['subClassOf'], entity))

    for s in [encode_ontology('Language'), encode_ontology('Technology'), encode_ontology('Concept')]:
        triple = s, rdfs['subClassOf'], instrument
        graph.add(triple)

        #TODO Check again with Ralf and Andrei
        triple = s, rdfs['subClassOf'], wikipage
        graph.add(triple)

    # Add remaining classes
    for s in ['Contribution', 'Contributor', 'Feature', 'Script', 'Course']:
        s = encode_ontology(s)
        triple = (s, rdfs['subClassOf'], entity)
        graph.add(triple)
        #TODO What about wiki pages?


def map_instance(page, graph):
    def class_for_page():
        if page['p']: return page['p']
        else: return 'Concept'

    clss = class_for_page()
    uri = encode_resource(clss, page['n'])

    triple = uri, rdf['type'], encode_ontology('WikiPage')
    graph.add(triple)

    triple = uri, rdf['type'], encode_ontology(clss)
    graph.add(triple)

    #TODO handle sub resources
    for sub in page.get('subresources', []):
        pass

    #Remaining predicates should all be in internal links
    for link in page.get('internal_links', []):
        # Determine predicate
        if '::' in link:
            predicate = link.split('::')[0]
            obj = disambiguate(link.split('::')[1])
        else:
            predicate = 'mentions'
            obj = disambiguate(link)

        if predicate not in ignored_keys_in_instances:
            triple = uri, encode_predicate(predicate), obj
            graph.add(triple)


def map_page(page, graph):
    is_instance = not 'isA' in page

    if is_instance:
        map_instance(page, graph)

def main():
    uri = 'http://triples.101companies.org/openrdf-sesame/repositories/Testing_2'
    serialized_version = 'graph.rdf'

    print 'Initializing graph'
    graph = rdflib.Graph()
    graph.bind('onto', 'http://101companies.org/ontology#')
    graph.bind('res', 'http://101companies.org/resources#')

    print 'Filtering wiki pages'
    wiki = filter_pages(Dumps.WikiDump())

    print 'Adding hardcoded (ontology) classes'

    print 'Adding ontology classes'
    make_ontology_classes(graph)

    # Building up cache to determine whether the relation is to a class or a instance
    # Do I really need this?
    for page in wiki:
        if 'isA' in page:
            if not page.get('p', None): link = page['p'] + ':' + page['n']
            else: link = 'Concept:' + page['n']
            classes_in_wiki.append(link)

    print 'Starting conversion'
    for page in wiki:
        map_page(page, graph)

    print 'Adding namespaces to graph'
    for key in namespace_cache.keys():
        graph.bind(key, namespace_cache[key])

    print 'Serializing graph...'
    open('graph.rdf', 'w').write(graph.serialize())

    print 'Clearing Sesame...'
    sesame.clear_graph(uri)

    print 'Uploading serialized file...'
    sesame.upload(uri, 'graph.rdf')

if __name__ == '__main__':
    print 'Starting process'
    main()
    print 'Finished... '
    #json.dump(erroneous_pages, open('./erroneous_pages.json', 'w'))
