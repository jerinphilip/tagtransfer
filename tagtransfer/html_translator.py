import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import cssselect
import tidylib
from lxml import html, etree

BASE_OPTIONS = {
  "indent": 1,           # Pretty; not too much of a performance hit
  "tidy-mark": 0,        # No tidy meta tag in output
  "wrap": 0,             # No wrapping
  "alt-text": "",        # Help ensure validation
  "doctype": 'html5',   # Little sense in transitional for tool-generated markup...
  "force-output": 1,     # May not get what you expect but you will get something
  "output-html": 1,
  "drop-empty-elements": 0,
  "drop-empty-paras": 0,
}

class FakeAnnotatedText:
    def __init__(self, text):
        self.text = text

class FakeResponse:
    def __init__(self, text):
        self.target = FakeAnnotatedText(text)

def convert(node):
    render = etree.tostring(node).decode("utf-8")
    tidy, errors = tidylib.tidy_fragment(render, BASE_OPTIONS)
    return tidy

class HTMLTranslator:
    def __init__(self, model_config, num_workers, cache_size, cache_mutex_buckets):
        # TODO(jerinphilip): Improve syntax upstream.
        config = ServiceConfig()
        config.numWorkers = num_workers;
        config.cacheSize = cache_size;
        config.cacheMutexBuckets = cache_mutex_buckets;

        self.service = Service(config)

        # What model are we using?
        self.model = self.service.modelFromConfigPath(model_config)


    def translate(self, page: str, bypass: bool = False):
        # Hardcode a bunch of options for now. TODO: improve
        options = ResponseOptions();
        options.alignment = True
        options.qualityScores = True
        options.HTML = True

        # Get nodes. Replace them in place.
        # document, errors = tidylib.tidy_document(page, BASE_OPTIONS)
        tree = html.fromstring(page)

        head = tree.xpath("/html/head")[0]
        for node in head.iterdescendants():
            if node.text is None:
                node.text = ''

        body = tree.xpath("/html/body")[0]
        for node in body.iterdescendants():
            if node.text is None:
                node.text = ''

        imgs = tree.xpath("/html//img")
        print("Images to begin with", len(imgs))

        node = html.fromstring(convert(body))
        imgs = node.xpath("//img")
        print("Images passed through tidy", len(imgs))

        if bypass:
            response = FakeResponse(convert(body))
            return self.postprocess(etree.tostring(head).decode("utf-8"), [None, response])
        else:
            responses = self.service.translate(self.model, bergamot.VectorString([convert(head), convert(body)]), options)
            return self.postprocess(etree.tostring(head).decode("utf-8"), responses)
        
    def postprocess(self, original_head, responses):
        head, body = responses
        node = html.fromstring(body.target.text)
        imgs = node.xpath("//img")
        print("Images at translated", len(imgs))
        embed = '<html> {}  {} </html>'.format(original_head, body.target.text)
        document, errors = tidylib.tidy_document(embed, BASE_OPTIONS)
        return document
