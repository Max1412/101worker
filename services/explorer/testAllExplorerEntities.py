from django.test import Client, TestCase
from json import loads
from unittest import skipIf
from urlparse import urlparse
import json
import os

# discovery provides some module path settings that are needed to import other
# modules.
import discovery

from mediawiki101 import wikifyNamespace


# Custom error classes, incase we can provide a more specific exception than the
# one thrown by the explorer.

class ResourceAlreadyAssignedError(Exception):
    pass

class ResponseStatusNotOkError(Exception):
    pass

class WrongClassifierError(Exception):
    pass

class WrongNameError(Exception):
    pass

# Descriptions to all possible error types
# These are output as is after each exception listing, so they may contain html
# code. Newline are repalce with <br>-Tags automatically
error_descriptions = {
    'ResourceAlreadyAssignedError':
        "This errors occurs if a link to an entity is found, and the link was "
        "already found for an entity higher up in the hierarchy.\n\n"
        "For Example: The top-level Root-Entity has the URL <code>/</code>, if "
        "further down a link to another entity is found, with exactly that"
        " url, it is assumed that the link generation is faulty, instead of "
        "that one url points to two different entities.",
    'ResponseStatusNotOkError':
        "This error occurs if a http response is not served with message "
        "<code>200 Ok</code>.",
    'WrongClassifierError':
        "This error occurs if the link to an entity specifies another expected "
        "classifier than the entity itself reports.",
    'WrongNameError':
        "This error occurs if the link to an entity specifies another expected "
        "name than the entity itself reports.",
    'ResourceNotFoundException':
        "This error occurs if the explorer script somehow deems an url "
        "invalid, and throws this exception by hand to trigger a "
        "<code>404 not found</code>.\n\n"
        "This is fine behaviour for nonsensical URLs. But no page in the "
        "explorer should produce a link to page that contains this exception.",
    'ValidationError':
        "This error is thrown by the explorer intern page validation code, "
        "that validates each entities output against a schema."
}

class Entity:
    def __init__(self, resource, classifier, name):
        self.resource = self.get_resource_url(resource)
        self.classifier = classifier
        self.name = name

    def __str__(self):
        return "Entity: (resource: {}, classifier: {}, name: {})".format(
            self.resource, self.classifier, self.name)

    def get_resource_url(self, resource):
        url = urlparse(resource)
        resource = url.path
        if resource[-1:] == '/':
            resource = resource[:-1]
        return resource


class Result:
    def __init__(self):
        self.error_dict = {}
        self.number_dict = {}
        self.total_count = 0

    # Result convert to True if it contains atleast one error
    # Requires crunch_numbers to be run already
    def __bool__(self):
        return self.total_count
    __nonzero__=__bool__

    def add_result(self, msg):
        entity, error = msg
        error_type = type(error).__name__
        if error_type not in self.error_dict:
            self.error_dict[error_type] = []
        self.error_dict[error_type].append({
            'entity': entity,
            'error': error,
        })

    def crunch_numbers(self):
        for error_type in self.error_dict:
            count = len(self.error_dict[error_type])
            self.number_dict[error_type] = count
            self.total_count += count


class Checker:
    def __init__(self):
        self.root_entities = [Entity("/discovery", "Namespace", "Namespace")]
        self.namespace_entities = []
        self.member_entities = []
        self.folder_entities = []
        self.file_entities = []
        self.fragment_entities = []

        self.assigned_resources = set()

        self.root_results = Result()
        self.namespace_results = Result()
        self.member_results = Result()
        self.folder_results = Result()
        self.file_results = Result()
        self.fragment_results = Result()

        self.client = Client()

    def check_all_entities(self):
        self.check_root_entities()
        self.check_namespace_entities()
        self.check_member_entities()
        self.check_folder_entities()
        self.check_file_entities()
        self.check_fragment_entities()

        # Build dict of results:
        self.results = {
            'root_errors': self.root_results,
            'namespace_errors': self.namespace_results,
            'member_errors': self.member_results,
            'folder_errors': self.folder_results,
            'file_errors': self.file_results,
            'fragment_errors': self.fragment_results
        }
        return self.results


    def check_root_entities(self):
        for root_entity in self.root_entities:
            (response, error) = self.check_entity(root_entity)
            if error:
                self.root_results.add_result((root_entity, error))
                continue
            for member in response['members']:
                self.namespace_entities.append(Entity(
                    member['resource'], member['classifier'], member['name']))

    def check_namespace_entities(self):
        for namespace_entity in self.namespace_entities:
            (response, error) = self.check_entity(namespace_entity)
            if error:
                self.namespace_results.add_result((namespace_entity, error))
                continue
            for member in response['members']:
                self.member_entities.append(Entity(
                    member['resource'], member['classifier'], member['name']))

    def check_member_entities(self):
        for member_entity in self.member_entities:
            (response, error) = self.check_entity(member_entity)
            if error:
                self.member_results.add_result((member_entity, error))
                continue
            for folder in response['folders']:
                self.folder_entities.append(Entity(
                    folder['resource'], folder['classifier'], folder['name']))
            for file in response['files']:
                self.file_entities.append(Entity(
                    file['resource'], file['classifier'], file['name']))

    def check_folder_entities(self):
        for folder_entity in self.folder_entities:
            (response, error) = self.check_entity(folder_entity)
            if error:
                self.folder_results.add_result((folder_entity, error))
                continue
            for folder in response['folders']:
                self.folder_entities.append(Entity(
                    folder['resource'], folder['classifier'], folder['name']))
            for file in response['files']:
                self.file_entities.append(Entity(
                    file['resource'], file['classifier'], file['name']))

    def check_file_entities(self):
        for file_entity in self.file_entities:
            (response, error) = self.check_entity(file_entity)
            if error:
                self.file_results.add_result((file_entity, error))
                continue
            for fragment in response['fragments']:
                self.fragment_entities.append(Entity(
                    fragment['resource'], fragment['classifier'], fragment['name']))

    def check_fragment_entities(self):
        for fragment_entity in self.fragment_entities:
            (response, error) = self.check_entity(fragment_entity)
            if error:
                self.fragment_results.add_result((fragment_entity, error))
                continue
            for fragment in response['fragments']:
                self.fragment_entities.append(Entity(
                    fragment['resource'], fragment['classifier'], fragment['name']))

    def check_entity(self, entity):
        # print 'checking', entity.resource

        if entity.resource in self.assigned_resources:
            return None, ResourceAlreadyAssignedError(
                "resource url was already assigned to another entity")
        self.assigned_resources.add(entity.resource)

        try:
            # For some reason this call still produces Tracebacks if we catch
            # the exception further down, how to supress these?
            response = self.client.get(entity.resource,
                                       {'format': 'json', 'validate': 'true'})

        except Exception as exception:
            return None, exception

        if response.status_code != 200:
            return response, \
                   ResponseStatusNotOkError(
                       "Did not return status ok (200) but instead (" +
                        str(response.status_code) + ")")

        parsed_response = loads(response.content)
        parsed_classifier = parsed_response['classifier']
        parsed_name = parsed_response['name']
        wikified_name = wikifyNamespace(parsed_name)
        if wikified_name and wikified_name != 'None':
            parsed_name = wikified_name

        if entity.classifier != parsed_classifier:
            return None, WrongClassifierError(
                "Did not have expected classifier '{} but instead '{}'".format(
                    entity.classifier, parsed_classifier))
        if entity.name != parsed_name:
            return None, WrongNameError(
                "Did not have expected name '{}' but instead '{}'".format(
                    entity.name, parsed_name))
        return parsed_response, None


@skipIf("TEST_ALL_EXPLORER_ENTITIES" not in os.environ,
        "This module is run from the 101worker module testAllExplorerEntities.")
class AllEntitiesTest(TestCase):
    results = None

    @classmethod
    def setUpClass(cls):
        checker = Checker()
        cls.results = checker.check_all_entities()

        log = {
            'total_count': 0,
            'error_descriptions': error_descriptions
        }

        def add_result(result_name):
            result = cls.results[result_name]
            result.crunch_numbers()
            log[result_name] = {
                'total_count': result.total_count,
                'error_counts': result.number_dict,
                'error_list': result.error_dict,
            }
            log['total_count'] += result.total_count

        add_result('root_errors')
        add_result('namespace_errors')
        add_result('member_errors')
        add_result('folder_errors')
        add_result('file_errors')
        add_result('fragment_errors')

        # print json.dumps(log, cls=LogEncoder, sort_keys=True, indent=4, separators=(',', ': '))
        outpath = os.path.join(os.environ['worker101dir'],
                               'modules', 'testAllExplorerEntities',
                               'results.json')
        with open(outpath, 'w') as outfile:
            json.dump(log, outfile, cls=LogEncoder, sort_keys=True, indent=4)

    # I get an error for some reason if this definition is left out
    @classmethod
    def tearDownClass(cls):
        pass

    # the following methods just signal to a human test executor were
    # errors happened

    def test_root(self):
        if AllEntitiesTest.results['root_errors']:
            self.fail()

    def test_namespaces(self):
        if AllEntitiesTest.results['namespace_errors']:
            self.fail()

    def test_members(self):
        if AllEntitiesTest.results['member_errors']:
            self.fail()

    def test_folders(self):
        if AllEntitiesTest.results['folder_errors']:
            self.fail()

    def test_files(self):
        if AllEntitiesTest.results['file_errors']:
            self.fail()

    def test_fragments(self):
        if AllEntitiesTest.results['fragment_errors']:
            self.fail()


# Custom JSON encoder
class LogEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return obj.__dict__
        if isinstance(obj, Exception):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
