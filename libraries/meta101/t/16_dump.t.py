from TAP.Simple import *
import meta101

plan(3)


eq_ok(meta101.Matches().dump(), {
          "rules"      : {},
          "matches"    : [],
          "failures"   : {},
      }, "matches dump");

eq_ok(meta101.Predicates().dump(), {
          "rules"      : {},
          "matches"    : [],
          "failures"   : {},
          "predicates" : [],
      }, "predicates dump");

eq_ok(meta101.Fragments().dump(), {
          "rules"      : {},
          "matches"    : [],
          "failures"   : {},
      }, "fragments dump");