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
[lemonade/pulL#13](https://github.com/jerinphilip/lemonade/pull/13/). The
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
[src] >  Change the Content Layout in <ph>Community Builder</ph>
[hyp] >  Ändern Sie das Content-Layout in <ph>Community Builder</ph>
[tgt] >  Ändern des Inhaltslayouts im <ph>Community-Generator</ph>

[src] >  <b>Max Values Displayed</b> – Specify how many groups display in the funnel chart.
[hyp] >  <b>Max Values Displayed</b> – Geben Sie an, wie viele Gruppen im Trichterdiagramm angezeigt werden.<b></b>
[tgt] >  <b>Angezeigte Höchstwerte</b>: Geben Sie an, wie viele Gruppen im Trichterdiagramm angezeigt werden.

[src] >  First, use field-level security to specify which users can see the <parmname>Question from Chatter</parmname> field on case detail pages.
[hyp] >  Verwenden Sie zunächst die Sicherheit auf Feldebene, um zu zeigen, welche Benutzer die <parmname>Frage aus dem</parmname> Chatter-Feld auf den Detailseiten des Falldetails sehen können.
[tgt] >  Geben Sie zuerst über die Feldebenensicherheit an, welche Benutzer das Feld <parmname>Frage aus Chatter</parmname> auf Kundenvorgangs-Detailseiten sehen können.

[src] >  <uicontrol>Execute in Browser</uicontrol>: The file, regardless of file type, is displayed and executed automatically when accessed in a browser or through an HTTP request.
[hyp] >  <uicontrol>Ausführung im Browser:</uicontrol> Die Datei, unabhängig vom Dateityp, wird automatisch angezeigt und ausgeführt, wenn sie in einem Browser oder über eine HTTP-Anfrage aufgerufen wird.
[tgt] >  <uicontrol>In Browser ausführen</uicontrol>: Die Datei wird unabhängig vom Dateityp angezeigt und automatisch ausgeführt, wenn sie in einem Browser oder über eine HTTP-Anforderung geöffnet wird.

[src] >  Select the 1-column layout, then click <uicontrol>OK</uicontrol>.
[hyp] >  Wählen Sie das 1-Spalten-Layout und klicken Sie auf OK.
[tgt] >  Wählen Sie das einspaltige Layout aus und klicken Sie dann auf <uicontrol>OK</uicontrol>.
```


## TODO

- [ ] Crawl web and test on random HTML segments.
- [ ] Evaluation methodology to compare multiple HTML tag-transfer methods following [Automatic Bilingual Markup Transfer](https://aclanthology.org/2021.findings-emnlp.299.pdf).
- [ ] Simplify instructions to run code in this repository.

