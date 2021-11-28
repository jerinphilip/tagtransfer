# tagtransfer


This repository uses
[bergamot-translator](https://github.com/browsermt/bergamot-translator), and
pybindings currently provisioned in
[lemonade](https://github.com/jerinphilip/lemonade/pull/13/) to test and
evaluate the HTML
translation functionality, where-in
the tags in source-text are transferred to a translated target sentence.


## Instructions to setup


First download an XML marked-up dataset from
[salesforce/localization-xml-mt](https://github.com/salesforce/localization-xml-mt).
This can be done by using:

```
bash scripts/download-data.sh ./
```

Next, copy the generated python-binding built shared library `.so` file built from
[lemonade/pull#13](https://github.com/jerinphilip/lemonade/pull/13/). The
library has to be built due to `-march=native` being present in builds, which
takes advantage of vector-instructions to speed up translations.

On the author's system, with a virtual environment using python3 in the current
folder, an example looks like:

```
cp ../lemonade/build/pybergamot.cpython-39-x86_64-linux-gnu.so env/lib/python3.9/site-packages/
```


To run the existing script, which simply translates the xml-marked-up
translation dataset, please use the following command:

```
python3 -m tagtransfer.main \
   --source-data localization-xml-mt-master/data/ende/ende_en_dev.json \
   --target-data localization-xml-mt-master/data/ende/ende_de_dev.json \
   --model-config ~/.local/share/lemonade/models/ende.student.tiny11/config.bergamot.yml
```

To download the model and configuration mentioned above, you may use
[lemonade/scripts/model\_manager.py](https://github.com/jerinphilip/lemonade/blob/unstable/scripts/model_manager.py)


If all works well, the output looks something like the following:

```
[src] >  <xref>Partner Profiles</xref>, <xref>Roles</xref>, and
[hyp] >  <xref>Partner Profile,</xref> <xref>Rollen</xref> und
[tgt] >  Überlegungen zu <xref>Partnerprofilen</xref>, <xref>Rollen</xref> und zur
With tags:  BLEU = 58.55 89.5/77.8/58.8/43.8 (BP = 0.900 ratio = 0.905 hyp_len = 19 ref_len = 21)
Without tags:  BLEU = 26.65 60.0/50.0/33.3/25.0 (BP = 0.670 ratio = 0.714 hyp_len = 5 ref_len = 7)
Matches perfectly?  Yes

[src] >  To view a saved call log, click the call log's <parmname>Subject</parmname>.
[hyp] >  Um ein gespeichertes Anrufprotokoll anzuzeigen, klicken Sie auf <parmname>das Thema des</parmname> Anrufprotokolls.
[tgt] >  Um ein gespeichertes Anrufprotokoll anzuzeigen, klicken Sie beim Anrufprotokoll auf <parmname>Anruf</parmname>.
With tags:  BLEU = 57.29 81.0/65.0/52.6/38.9 (BP = 1.000 ratio = 1.050 hyp_len = 21 ref_len = 20)
Without tags:  BLEU = 54.37 71.4/53.8/50.0/45.5 (BP = 1.000 ratio = 1.077 hyp_len = 14 ref_len = 13)
Matches perfectly?  Yes

[src] >  From the home page, select <menucascade><uicontrol>Create</uicontrol> <uicontrol>Dashboard</uicontrol></menucascade>.
[hyp] >  Wählen Sie von der Startseite <menucascade><uicontrol>das</uicontrol> <uicontrol>Dashboard</uicontrol></menucascade> erstellen.
[tgt] >  Wählen Sie auf der Startseite <menucascade><uicontrol>Erstellen</uicontrol><uicontrol>Dashboard</uicontrol></menucascade>.
With tags:  BLEU = 76.36 90.0/79.3/71.4/66.7 (BP = 1.000 ratio = 1.034 hyp_len = 30 ref_len = 29)
Without tags:  BLEU = 14.26 55.6/25.0/7.1/4.2 (BP = 1.000 ratio = 1.286 hyp_len = 9 ref_len = 7)
Matches perfectly?  Yes

[src] >  Click <uicontrol>Show Dependencies</uicontrol> to display the items, such as another component, permission, or preference, that must exist for this custom component to be valid.
[hyp] >  Klicken Sie auf <uicontrol>Abhängigkeiten anzeigen,</uicontrol> um die Elemente anzuzeigen, z. B. eine andere Komponente, eine Berechtigung oder eine andere Präferenz, die vorhanden sein muss, damit diese benutzerdefinierte Komponente gültig ist.
[tgt] >  Klicken Sie auf <uicontrol>Abhängigkeiten anzeigen</uicontrol>, um die Elemente (beispielsweise eine weitere Komponente, Berechtigung oder Einstellung) anzuzeigen, die vorhanden sein müssen, damit diese benutzerdefinierte Komponente gültig ist.
With tags:  BLEU = 46.93 75.6/56.8/39.5/28.6 (BP = 1.000 ratio = 1.125 hyp_len = 45 ref_len = 40)
Without tags:  BLEU = 48.99 71.1/56.8/41.7/34.3 (BP = 1.000 ratio = 1.152 hyp_len = 38 ref_len = 33)
Matches perfectly?  Yes
```


## TODO

- [ ] Crawl web and test on random HTML segments.
- [ ] Evaluation methodology to compare multiple HTML tag-transfer methods following [Automatic Bilingual Markup Transfer](https://aclanthology.org/2021.findings-emnlp.299.pdf).
- [ ] Simplify instructions to run code in this repository.

