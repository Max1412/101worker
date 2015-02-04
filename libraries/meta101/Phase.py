import abc
import json
import os
import re
import incremental101
from   .util          import stripregex, tolist


class Phase(object):
    __metaclass__ = abc.ABCMeta


    def __init__(self, rules={}):
        self.rules    = rules
        self.matches  = []
        self.failures = []


    @abc.abstractmethod
    def suffix(self):
        pass

    @abc.abstractmethod
    def applicable(self, rule):
        pass

    def dump(self):
        return {
            "matches"  : self.matches,
            "failures" : self.failures,
            "rules"    : self.rules,
        }


    def run(self):
        repodir   = os.environ[   "repo101dir"]
        targetdir = os.environ["targets101dir"]
        switch    = {"A" : self.onfile, "M" : self.onfile, "D" : self.ondelete}

        for op, path in incremental101.gendiff():
            if path.startswith(repodir):
                target  = path.replace(repodir, targetdir, 1) + self.suffix()
                switch[op](target  =target,
                           filename=path,
                           dirname =os.path.dirname(path)[len(repodir):],
                           basename=os.path.basename(path))

        return self.dump()


    def onfile(self, **kwargs):
        units = []

        for index, value in enumerate(self.rules):
            rule   = value["rule"]
            result = self.match(index, rule, **kwargs)
            if result and "metadata" in rule:
                for metadata in tolist(rule["metadata"]):
                    result["metadata"] = metadata
                    units.append(result.clone())

        # TODO fix this dominator code
        keys     = []
        for unit in units:
            metadata = unit["metadata"]
            if "dominator" in metadata:
                keys.append(metadata["dominator"])
        removals = []
        for key in keys:
            for unit in units:
                metadata = unit["metadata"]
                if key in metadata \
                and ("dominator" not in metadata
                     or metadata["dominator"] != key):
                    removals.append(unit)
        survivals = []
        for unit in units:
            if not unit in removals:
                survivals.append(unit)
        units = survivals

        incremental101.writejson(target, units)
        if units:
            self.matches.append({
                "filename" : kwargs["filename"],
                "units"    : units,
            })


    def ondelete(self, target, **kwargs):
        incremental101.deletefile(target)


    def match(self, index, rule, **kwargs):
        if not self.applicable(rule):
            return None

        kwargs["result"] = {"id" : index}
        for key in rule:
            func = getattr(self, "check" + key, None)
            if func and not func(rule[key], key=key, rule=rule, **kwargs):
                return None

        return kwargs["result"]


    def checksuffix(self, suffixes, basename, **kwargs):
        return any(basename.endswith(suffix) for suffix in tolist(suffixes))


    def checkcontent(self, pattern, filename, **kwargs):
        with open(filename) as f:
            return re.search(stripregex(pattern, pattern), f.read())


    def matchnames(self, values, path):
        def matchname(want):
            pattern = stripregex(want)
            return re.search(pattern, path) if pattern else path == want
        return any(matchname(v) for v in tolist(values))

    def checkfilename(self, values, filename, **kwargs):
        return self.matchnames(values, filename)

    def checkbasename(self, values, basename, **kwargs):
        return self.matchnames(values, basename)

    def checkdirname(self, values, dirname, **kwargs):
        return self.matchnames(values, dirname)
