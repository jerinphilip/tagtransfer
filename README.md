# tagtransfer


This repository uses
[bergamot-translator](https://github.com/browsermt/bergamot-translator), and
pybindings currently provisioned in
[lemonade](https://github.com/jerinphilip/lemonade) to experiment with the
HTML translation functionality where-in the tags in source-text are transferred
to a translated target sentence.

Currently this repository houses:

1. Minimal setup for evaluating HTML using
   [salesforce/localization-xml-mt](https://github.com/salesforce/localization-xml-mt).
2. A Web Service that allows rendering translated HTML by supplying only the
   source-url to inspect visually how well the HTML is being translated. 


For a visual sample of how good the render of the translated page is checkout
[The Hindu](https://www.thehindu.com/) translated to German from English below:

<img width="720" alt="image" src="https://user-images.githubusercontent.com/727292/148254241-d658706f-b99a-4b65-a422-a9d336a550a0.png">


## Instructions to setup

### Install reqiurements

We need `requests` for work with webpages, a few `html` parsing libraries and
`bergamot` all of which is currently in `requirements.txt`. Using a virtual
environment is recommended.

```
# (Installs flask, lxml, requests, bergamot)
python3 -m pip install bergamot
```

To download the models and associated configuration files required to run
applications in this repository, you may use the package-manager in bergamot
python module.


```bash
$ bergamot download # fetches available models
$ bergamot ls

The following models are available:

    1. cs-en-base Czech-English base
    2. cs-en-tiny Czech-English tiny
    3. en-cs-base English-Czech base
    4. en-cs-tiny English-Czech tiny
    5. en-de-base English-German base
    6. en-de-tiny English-German tiny
    7. es-en-tiny Spanish-English tiny
    8. en-es-tiny English-Spanish tiny
    9. et-en-tiny Estonian-English tiny
   10. en-et-tiny English-Estonian tiny
   11. is-en-tiny Icelandic-English tiny
   12. nb-en-tiny Norwegian (Bokmal)-English tiny
   13. nn-en-tiny Norwegian (Nynorsk)-English tiny
   14. de-en-base German-English base
   15. de-en-tiny German-English tiny

```

### Launching HTML translation service

The HTML rendering is through a python script which launches a local-server.
The local-server takes the page, translates and renders via flask the
translated web-page. There are some adjustments to get the links correct so
resources (css, images) load and page-flow is not affected.

To start the web-service locally:

```

# To run
python3 -m tagtransfer.webapp --num-workers 4
``` 

Assuming the app is launched in `localhost:8080`, which model to choose,
whether to use an additional model to pivot and the URL to translate is
controlled by the following `GET` args.

```
url       url to translate
model     model-code to use in forward translation
pivot     model-code to use in pivoting after forward translation. This is optional.
bypass    Easy switch to bypass translation and render the original page, useful
          in debugging.
use_tidy  use 3rd-party HTML5 sanitization library to no crash when malformed
          HTML is sent to pipeline.  
```

Model codes can be chosen from those listed above via `bergamot ls`.

Here's an example link:
* http://localhost:8080/?url=https://www.thehindu.com&model=en-de-tiny&pivot=de-en-tiny&bypass=false&use_tidy=true

Once the app is launched, links are modified to go through the translator again
so as to conveniently check if translation works in a browsing workflow.


Known downsides of running through python is sessions and single-page apps
dependent heavily on JavaScript altering DOM will not work well with this
mechanism. But from a development perspective, static pages are just as fine
enough to capture enough HTML that causes issues in the pipeline to propogate a
fix upstream.


### Evaluating markup via xml-localization-dataset

(This is still in early stages)

First download an XML marked-up dataset from
[salesforce/localization-xml-mt](https://github.com/salesforce/localization-xml-mt).
This can be done by using:

```
bash scripts/download-data.sh 
```


To run the existing script, which simply translates the xml-marked-up
translation dataset, please use the following command:

```
python3 -m tagtransfer.xml_eval                                        \
   --dataset-dir data/localization-xml-mt-master/data/
```

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


