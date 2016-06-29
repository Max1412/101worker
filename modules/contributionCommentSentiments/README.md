# contributionCommentSentiments

A module to extract comments, preprocess those comments, and analyze their sentiments
on a per-contribution basis.

This module is needed for our main module _commentSentiments_,
please see its readme for more details and the rest of the documentation
regarding results and analysis of the results.
https://github.com/alexsr/101worker/tree/master/modules/featuresPerContribution

## Assumptions

This module assumes the following things:
* A sentence with three or less words does not contain much of a sentiment.
* All comments found in the source code of contributions are somewhat
reasonable.
* All comments found in the source code of contributions are some kind of
sentence or at least close to a sentence.

## Details

The module generates a "contributionCommentSentiments.json" dump, which consists 
of a summary of all generated data regarding the comments and their sentiments
of the contribution. Even if it works on a per-contribution basis, this
is a generated dump (and not a secondary resource).

Example:
```json
{
    "javaComposition": {
        "nonNeutralScores": {
            "pos": 1.039,
            "neu": 3.702,
            "neg": 0.259,
            "compound": 1.0601
        },
        "averageNonNeutral": {
            "pos": 0.20779999999999998,
            "neu": 0.7404,
            "neg": 0.0518,
            "compound": 0.21202000000000001
        },
        "averageScores": {
            "pos": 0.04722727272727272,
            "neu": 0.9410000000000001,
            "neg": 0.011772727272727273,
            "compound": 0.04818636363636364
        },
        "sentences": 22,
        "scores": {
            "pos": 1.039,
            "neu": 20.702,
            "neg": 0.259,
            "compound": 1.0601
        },
        "tooShortSentences": 9,
        "nonNeutralSentences": 5
    },
    ...
```

This is a subset of the complete dump, the part that contains all
info about the contribution _javaComposition_, to be exact.
The values mean the following:
* Sentences: Number of total sentences extracted from the comments of the source code
* nonNeutralSentences: Number of sentences with a neutral score other than 1.0 
* tooShortSentences: Number of sentences that have been filtered out because they have only three or less words in them.
* Scores: The accumulated scores
* averageScores: The accumulated scores divided by the number of sentences taken into account
* nonNeutralScores: The accumulated scores of all non-neutral sentences
* averageNonNeutral: The accumulated scores of all non-neutral sentences divided by the number of non-neutral sentences

Please note that this module is also extracting all comments from the source
code, but does not generate an output for the comments.
The supported languages are:
java, c++, go, haskell, python, ruby, html,  php, scala, javascript, perl
and many more that use the same commentary conventions as those.

## Dependencies

This module uses the files of the contributions and does not need any dumps.
You need to have the following (additional) pip-packages installed before running this module:
* nltk

The necessary word lists for nltk-vader are downloaded automatically the first time
the module is run.

## Issues

None.