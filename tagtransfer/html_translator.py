import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import cssselect
from lxml import html, etree
from bergamot.config import repository
import typing as t
import requests
import tidylib


def convert(node):
    return etree.tostring(node, method="html", encoding="utf-8").decode("utf-8")


BASE_OPTIONS = {
    "indent": 1,  # Pretty; not too much of a performance hit
    "tidy-mark": 0,  # No tidy meta tag in output
    "wrap": 0,  # No wrapping
    "alt-text": "",  # Help ensure validation
    "doctype": "html5",  # Little sense in transitional for tool-generated markup...
    "force-output": 1,  # May not get what you expect but you will get something
    "output-html": 1,
    "drop-empty-elements": 0,
    "drop-empty-paras": 0,
}


class HTMLTranslator:
    def __init__(self, num_workers, cache_size):
        config = ServiceConfig(
            numWorkers=num_workers,
            cacheSize=cache_size,
            cacheMutexBuckets=num_workers,
        )

        self.service = Service(config)

        # What model are we using?

        self.cache = {}

    def translate(
        self, model: str, pivot: t.Union[str, None], page: str, bypass: bool = False
    ):
        options = ResponseOptions(HTML=True)

        # Get nodes. Replace them in place.
        def tidy(tree):
            page = convert(tree)
            tidypage, errors = tidylib.tidy_document(page, BASE_OPTIONS)
            modtree = html.fromstring(tidypage)
            return convert(modtree)

        tree = html.fromstring(page)

        if bypass:
            return self.postprocess(convert(tree))
        else:
            response = None
            if pivot is not None:
                source_to_pivot_model = self.get_model(model)
                pivot_to_target_model = self.get_model(pivot)
                [response] = self.service.pivot(
                    source_to_pivot_model,
                    pivot_to_target_model,
                    # bergamot.VectorString([convert(tree)]),
                    bergamot.VectorString([tidy(tree)]),
                    options,
                )
            else:
                forward_model = self.get_model(model)
                [response] = self.service.translate(
                    forward_model,
                    # bergamot.VectorString([convert(tree)]),
                    bergamot.VectorString([tidy(tree)]),
                    options,
                )

            return self.postprocess(response.target.text)

    def get_model(self, code):
        if code not in self.cache:
            config = repository.modelConfigPath(code)
            self.cache[code] = self.service.modelFromConfigPath(config)
        return self.cache[code]

    def postprocess(self, text):
        return text

    def intercept(self, url):
        response = requests.get(
            url,
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
            },
        )

        document = response.text
        # Little hack for now: decode &#160; etc entities because we don't support those
        # document = re.sub(r"&#\d+;", lambda match: unescape(match[0]), document)

        # Add <base href=""> to <head>
        tree = html.fromstring(document)
        head = tree.xpath("/html/head")[0]
        head.insert(
            1, html.fragment_fromstring('<base href="{}" target="_parent">'.format(url))
        )

        return etree.tostring(
            tree, method="html", pretty_print=True, encoding="utf-8"
        ).decode()

    def translate_url(self, model1: str, model2: str, url: str, bypass: bool = False):
        # Intercept the URL to obtain source and show translation
        document = self.intercept(url)

        # Translate document HTML
        translated = self.translate(
            model1,
            model2,
            document,
            bypass,
        )

        return f"<!DOCTYPE html>\n{translated}"
