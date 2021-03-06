__author__ = 'avaranovich'

import os
from connection import Connection
from jinja2 import Environment, FileSystemLoader
import urllib2
from json import loads, load
import sys

SPATXT = 'text/boolean'


def process(file_names, prefixes):
    for query_file in file_names:
        template_file = query_file.replace('sparql', 'tmpl')
        if query_file == '' or template_file == '':
            continue
        print query_file
        with open(os.path.join(os.path.dirname(__file__), 'sparql', query_file)) as f:
            query = f.read()
            #print query
            if query_file == "baselineContribution.sparql":
                infer = False
            else:
                infer = True

            if not infer:
                res = connection.query(query, inference=False)
            else:
                if "ASK" in query:
                  res = connection.query(query, SPATXT)
                else:
                    res = connection.query(query)
            print res


            file_to_save = template_file
            if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'templates', template_file)):
                template_file = "default.tmpl"

            template = env.get_template(template_file)

            def unqualify(x):
                return escape(prefixy(x)).split(':')[1]
                
            def escape(x):
                return x.replace('_', "\_").replace('#', "\#")
                
            def prefixy(x):
                for ns in prefixes:
                    if ns in x:
                        x = x.replace(ns, prefixes[ns]+':')
                return x
            try:		
            	output = template.render(data=res, prefixy=lambda x: prefixy(x), unqualify=lambda x: unqualify(x), escape=lambda x: escape(x))
            except:
	    	output = ""
	    #print output

            with open(os.path.join(os.path.dirname(__file__), 'output', file_to_save.replace('.tmpl', '.txt')), "w") as output_file:
                output_file.write(output)

            #print res

if __name__=='__main__':

    env = Environment(loader=FileSystemLoader('templates'))
    connection = Connection('http://triples.101companies.org:8080/openrdf-sesame/')
    connection.use_repository('sandbox')

    with open('../onto2ttl/config.json') as json_data:
        m = load(json_data)
        for x in m['@context']:
            connection.addnamespace(x, m['@context'][x])

    req = urllib2.Request('http://triples.101companies.org:8080/openrdf-workbench/repositories/sandbox/namespaces')
    req.add_header('Accept', 'application/sparql-results+json')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    sock = urllib2.urlopen(req)
    #print "INFO", sock.info()
    data = sock.read()
    #print "DATA", data
    sock.close()
    prefixes = dict()

    for b in loads(data)['results']['bindings']:
        prefix = b['prefix']['value']
        ns = b['namespace']['value']
        prefixes[ns] = prefix

    if len(sys.argv) == 2:
        print "Processing file: %s" % sys.argv[1]
        file_names = [sys.argv[1]]
    else:
       relevant_path = os.path.join(os.path.dirname(__file__), 'sparql')
       included_extenstions = ['sparql']
       file_names = [fn for fn in os.listdir(relevant_path) if any([fn.endswith(ext) for ext in included_extenstions])]

    process(file_names, prefixes)



