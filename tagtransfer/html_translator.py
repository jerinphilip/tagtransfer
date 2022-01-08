import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import cssselect
from lxml import html, etree
from bs4 import BeautifulSoup
from bergamot.config import repository
import typing as t
import requests
import tidylib

TIDY_PRESETS = {
    "indent": 1,  # Pretty; not too much of a performance hit
    "tidy-mark": 0,  # No tidy meta tag in output
    "wrap": 0,  # No wrapping
    "alt-text": "",  # Help ensure validation
    "doctype": "html5",  # Little sense in transitional for tool-generated markup...
    "force-output": 1,  # May not get what you expect but you will get something
    "output-html": 1,
    "drop-empty-elements": 0,
    "drop-empty-paras": 0,
    "show-body-only": "auto",
}


def make_soup(markup: str):
    return BeautifulSoup(markup, "html5lib")


def soup_to_html5_strict(soup: BeautifulSoup):
    text = soup.prettify(formatter="html5")
    return text


def soup_utf8_tx(soup: BeautifulSoup):
    text = soup.prettify(formatter="html5")
    return text.replace("&amp;", "&")


def soup_relaxed(soup):
    text = soup.prettify(formatter="minimal")
    return text.replace("&amp;", "&")


class HTMLTranslator:
    def __init__(self, num_workers, cache_size, use_tidy=True):
        config = ServiceConfig(
            numWorkers=num_workers,
            cacheSize=cache_size,
            cacheMutexBuckets=num_workers,
        )

        self.service = Service(config)

        # What model are we using?

        self.cache = {}
        self.use_tidy = use_tidy

    def intercept(self, url):
        soup = self._intercept(url)
        return soup_to_html5_strict(soup)

    def translate_url(self, model1: str, model2: str, url: str, bypass: bool = False):
        # Intercept the URL to obtain source and show translation
        soup = self._intercept(url)

        # Translate document HTML
        translated = self._translate(
            model1,
            model2,
            soup,
            bypass,
        )

        return soup_relaxed(translated)

    def translate(
        self, model: str, pivot: t.Union[str, None], page: str, bypass: bool = False
    ):
        soup = make_soup(page)
        translated_soup = self._translate(model, pivot, soup, bypass)
        return soup_relaxed(translated_soup)

    def _get_model(self, code):
        if code not in self.cache:
            config = repository.modelConfigPath(code)
            self.cache[code] = self.service.modelFromConfigPath(config)
        return self.cache[code]

    def _postprocess(self, soup, translated_body):
        translated_body = make_soup(translated_body)
        soup.body.replace_with(translated_body)
        return soup

    def _intercept(self, url):
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
        soup = make_soup(document)
        base_href = soup.new_tag("base", href=url, target="_parent")
        soup.head.insert(1, base_href)
        return soup

    def _translate(
        self,
        model: str,
        pivot: t.Union[str, None],
        soup: BeautifulSoup,
        bypass: bool = False,
    ):
        options = ResponseOptions(HTML=True)

        if bypass:
            return soup
        else:
            response = None
            if pivot is not None:
                source_to_pivot_model = self._get_model(model)
                pivot_to_target_model = self._get_model(pivot)
                [response] = self.service.pivot(
                    source_to_pivot_model,
                    pivot_to_target_model,
                    bergamot.VectorString([soup_utf8_tx(soup.body)]),
                    options,
                )
            else:
                forward_model = self._get_model(model)
                [response] = self.service.translate(
                    forward_model,
                    bergamot.VectorString([soup_utf8_tx(soup.body)]),
                    options,
                )

            return self._postprocess(soup, translated_body=response.target.text)
