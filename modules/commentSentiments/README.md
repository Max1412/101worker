# Zusätzliche Dokumentation

Für die "eigentliche" Dokumentation des Moduls, siehe unten.
Dies ist die zusätzliche Dokumentation gefordert in https://svn.uni-koblenz.de/softlang/pttcourse/ptt16/lab/doc_requs_ass03.pdf .

## Gruppeninfo
* Gruppenname: zuse (https://gitlab.uni-koblenz.de/zuse/pttss16/)
* Mitglieder: 

Alexander Scheid-Rehder, Anna Schneider, Benedikt Kraus, Maximilian Mader, Tim Liß

* Wie sind die Anforderungen für einen Bonus erfüllt worden?

Wir haben schon 2 mal einen Bonus erhalten, die Anforderungen der Vollständigkeit halber trotzdem:

### Anforderungen:
"all team members leave traces of their work on gitlab/github":
Siehe commits, bei diesem Assignment haben wir allerdings mehr zusammen an einem PC gearbeitet (à la 4 (oder mehr)-Augen-Programmierung))
Außerdem war etwas mehr Planungs- und Recherchearbeit als sonst nötig, die von den Mitlgiedern mit weniger/keinen commits übernommen wurde.

"the work is explained well in the README.md file which comes with the work":
Siehe diese Readme und die unten verlinkten Readmes.

"the limitations / underlying assumptions of the solution are explained well"
Ebenfalls, siehe "richtige" Dokumentation.

"the work applies concepts of "mining software data" correctly and understandably"
Wir arbeiten wie in "mining software data" vorgestellt: Nutzen von libraries wie
nltk, aufbereiten der Daten vor und nach der verarbeitung, Interpretation der Ergebnisse.


## Aufgabenbeschreibung
* Wie lautet die Aufgabenstellung? (In eigenen Worten)

Sentimentanalyse (Stimmungsanalye) auf Quellcode-Kommentare anwenden:
Extrahieren der Kommentare, aufbereiten der Kommentare,
so dass sie analysiert werden können (trennen/zusammenfügen von Sätzen),
Daten verarbeiten und dann interessante Zusammenhänge herausfinden und
zeigen, zum Beispiel als Diagramm.

* Welche Hypothesen können gemacht werden?

Die Hypothesen bezüglich der Auswertung werden in der "eigentlichen" Dokumentation
beschrieben, genau wie die Annahmen, auf denen unsere Module basieren.

* Welche Erwartungen habt ihr?

Wir erwarten, dass Quellcode-Kommentare nicht besonders "wertend" und
weitgehend neutral sind.
Wir erwarten außerdem, dass sich trotzdem ein gewisser Unterschied zwischen
den verwendeten Sprachen, den Contributors bzw. den Contributions feststellen lässt,
sind aber unentschlossen, in welche Richtung dieser ausfallen wird
(kurz gesagt, wir erwarten nicht speziell, dass beispielsweise Java-Kommentare positiver
als Haskell-Kommentare sind)

## Vorgehen
* Wie seid ihr vorgegangen?

Wir haben uns zuerst damit beschäftigt, die Kommentare aus dem Quellcode
zu extrahieren .
Dnmach haben wir diese aufbereitet, so dass wir ganze Sätze haben
(also Sätze, die über mehrere Zeilen gehen zusammengesetzt, Sätze getokenized usw.)
und haben unnötige Dinge rausgefiltert (@author-Tags usw.), um sie
mit nltk-vader zu analysieren.
(siehe Modul [contributionCommentSentiments](https://github.com/Max1412/101worker/tree/master/modules/contributionCommentSentiments))
Die analysierten Daten haben wir dann auf verschiedene Arten und Weisen
geplottet und gespeichert.

* Auf welche Schwierigkeiten seid ihr gestoßen?

Beim extrahieren der Kommentare war es schwierig, alle möglichen
Kommentare und Kommentar-Stile abzudecken, also nicht nur die Unterstützung 
für Kommentarzeichen in Programmiersprachen, aber etwa Kommentare, vor denen
Code oder Whitespace steht, Mulitiline-Kommentare als Block-Kommentare und
als nicht-Block-Kommentare, Kommentare die als Block in einer Code-Zeile
stehen (also z.B. "int a = /* comment */ 1" als Zeile).
All dies haben wir aber gelöst.

Beim analysieren der Daten fiel es uns schwer, geeignete statistische Mittel
und Wege zu finden, um darzustellen, was die Daten aussagen.

Außerdem ist es uns schwer gefallen, uns mit den anderen zwei Gruppen,
die dieselbe Aufgabe hatten, abzusprechen. Während eine Gruppe
sehr kommunikativ und kooperativ war und direkt vorgeschlagen hat,
sich mit einem Machine-Learning-Ansatz von uns abzuheben, hat sich die 
andere Gruppe bis Montag (zwei Tage vor Abgabe) nicht gemeldet und dann
auch nur sehr kurz gefasst.
Wir hoffen, unsere Lösung hebt sich genug von den anderen ab. Wir haben
unseren Code selbst geschrieben.

* Auf welche Aspekte habt ihr euch eingeschränkt und warum?

Die Kommentare sind auf die Programmiersprachen (mehr dazu siehe Modul-readme)
eingeschränkt. Wir haben uns auf die Programmiersprachen konzentriert,
mit denen die Test-Contributions geschrieben sind, und noch einige andere
mit abgedeckt.

* Welche Alternativen gibt es noch?

Alternative libraries, trainieren des sentiment-analyzer, Auswertung anderer
Daten, ...


## Dateimanagement
* Wo liegen die Dateien für das Assignment?

Repo: https://github.com/Max1412/101worker/

Module: 
https://github.com/Max1412/101worker/tree/master/modules/contributionCommentSentiments
https://github.com/Max1412/101worker/tree/master/modules/commentSentiments (siehe unten)

Readme:
diese Datei + Readmes der Module

* Was sind Input und Output? / Wie sind die Strukturen der Outputs?

Siehe Readmes der einzelnen Module. Dort werden Input und Output genannt
und mit Beispielen erklärt (siehe unten für dieses Modul)

## Auswertung
* Disskussion/Interpretation der Ergebnisse?

Beschreibung der Ausgabe in der _Details_-Section der Modul-Readmes
(für dieses Moduls siehe unten). Zusammenfassend lässt sich sagen
dass die Ergebnisse wegen der Einagbedaten nicht ideal sind,
sich aber trotzdem einiges ablesen lässt: So kommentieren
manche Programmierer der Module positiver, andere negativer als
der Durchschnitt. Die Diagramme an sich sind recht aussagekräftig,
werden allerdings noch mal genauer beschrieben (siehe unten)

* Welche Darstellungen/Abbildungen für die Ergebnisse wurden gewählt
und warum?

Wir haben uns für eine grafische Darstellung der Ergebnisse,
überwiegend als Säulendagramm, entschieden. So lassen sich
verschiedene Werte gut vergleichen und wir haben zusätzlich Linien für
Durchschnittswerte, damit man direkt sieht, ob ein Wert eher über- oder
utnerdurchschnittlich ist.

* Stimmen die Ergebnisse mit den Erwartungen überein und warum?

Unsere Erwartung, das Code-Kommentare oft recht neutral sind, hat sich bestätigt.
Für die Vergleiche von Programmiersprachen, Contributions und Contributors
hatten wir nicht wirklich spezielle Erwartungen, außer, dass es tatsächlich
Unterschiede geben wird. Das hat sich ebenfalls bewahrheitet

## Anleitung zur Ausführung
* Wie bringt man das Programm zum laufen?

Man installiert den 101worker (Anleitung siehe https://github.com/Max1412/101worker/)
und führt dann die Module mit ```python bin/run_module <module>```
aus. Module zum Ausführen: 
matchLanguage (bereits vohanden),
contributionCommentSentiments (von uns),
commentSentiments (von uns, Haupt-Modul),

* Gibt es Besonderheiten oder Abhängigkeiten?

Die Abhänigkeiten der einzelnen Module (inklusive benötigte pip-packages)
stehen in den readmes der jeweilgen Module.

* Was wurde alles getestet?

Alle unsere Module haben wie in Assignment 2 ihre eigenen Test-Cases.

## Dokumentation im Quellcode
* Ausreichende Kommentare im Source-Code?

Siehe Quellcode.



# commentSentiments

A module to process the contributionCommentSentiments dump
and combine its information with information found in the wiki,
such as the language or contributor of a given contribution.
This module does not just process the data, but also analyzes it and
saves its output in graphical and non-graphical form.

Necessary python packages for this module are:
* matplotlib
* numpy
* (nltk for contributionCommentSentiments, on which this module depends)

These must be installed before executing the module. 

This is the readme file for our *main* module _commentSentiments_.
We also implemented the following module, which is used to distribute the
work necessary for this module. README files for these modules are also available:
* _contributionCommentSentiments_ (https://github.com/Max1412/101worker/tree/master/modules/contributionCommentSentiments)

We also use the already present module _matchLanguage_.

The motivation to distribute the work into different modules was both to create useful information for others to use in the future and to have a clearer structure in this main module.

## Assumptions

No actual assumptions are made in this module as it is only
processing and displaying generated data, but the module contributionCommentSentiments,
on which this one depends makes some assumptions. Those can be read
in its readme file, which is available at the link above.

## Details

The module generates a ... dump, which consists
of ...

Here are the generated plots together with an analysis/evaluation of the result:
**Please note: For more accurate and/or representative results, more contributions must used to generate data
and all following "conclusions" are drawn from the analyzed contributions only**

![Contribution comment sentiments](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/contribution_comment_sentiments.png?raw=true)

This is the plot showing the average scores sorted by contribution.
As you can see, this plot does not show the the neutral score, for easier
comparison between the much lower positive and neutral values. The
compound value is a comprehension of the "positive vs negative" value of the
contribution. 
The thin horizontal lines are the average of positive, negative and the compound
in all contributions.

What does this image say about the contributions?
* On average, the comments are more negative than positive (see the horizontal lines)
* There are two contributions in the mix which contain no positive comments at all.
* Only one contribution is actually rated more positive than negative.
* Both Haskell contributions are very similar!
* _jdom_ and py3k are very similiar!

At this point we still "don't know", _why_ some contributions are more negative
than others or even similar... maybe this has something to do with languages or contributors?

![Language comment sentiments](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/language_comment_sentiments.png?raw=true)

This plot shows the same information as the previous one, but ordered by language.
This also combines the _jdom_ and _javaComposition_ contributions into _Java_.

Now we can see:
* Python is by far the "most negative language"
* Even with two very different contributions combined, Java is still very positive
* The Haskell contributions from the first figure are tagged with different
versions of haskell in the wiki

![Developer comment sentiments](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/developer_comment_sentiments.png?raw=true)

This figure shows the sentiments ordered by contributor/developer.

Now we can see:
* Comments by _rlaemmel_ are very close to neutral
* _tschmorleiz_ writes more positive than negative comments
* _DerDackel_ writes negative comments only

We also analyzed the ratio of non-neutral comments to total comments:
![Developer ratio](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/ratio_non%20neutral_sentences_to%20sentences_by_developer.png?raw=true)

This shows that _DerDackel_ writes not just only negative comments, but has also
many non-neutral comments in comparison with his overall comments.
We can also see that _tschmorleiz_ is a very neutral comment-writer.
But overall, those ratios are not at all very different, only by roughly 10%.

The ratio are also available per contribution and per language:
![Contribution ratio](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/ratio_non%20neutral_sentences_to%20sentences_by_contribution.png?raw=true)
![Language ratio](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/ratio_non%20neutral_sentences_to%20sentences_by_language.png?raw=true)

We also plotted the three figures from the beginning with the neutral
scores, but stripped of the completely neutral comments.
This means, in the following figures, only the non-neutral comments are
taken into account.

![Contribution non-neutral](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/non_neutral_contribution_comment_sentiments.png?raw=true)
![Language non-neutral](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/non_neutral_language_comment_sentiments.png?raw=true)
![Developer non-neutral](https://github.com/Max1412/101worker/blob/master/modules/commentSentiments/non_neutral_developer_comment_sentiments.png?raw=true)

What we can see here is, that even with no completely neutral sentences taken into account,
ne neutral scores outrank the positive/negative scores by far.
This means that even the positive or negative comments are **not strongly positive or negative**.
This actually confirms what we expected: Source-Code comments do not contain
very strong sentiments, and thus are basically very neutral. This is also confirmed
by the overall low ratios between neutral and non-neutral comments seen in the second type of figures.


## Dependencies

This module relies on the dump from the modules _matchLanguage_ and
_contributionCommentSentiments_ and their respective dependencies.
It also uses the wiki-links dump.

## Issues

None.