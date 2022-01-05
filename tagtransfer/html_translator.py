import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import cssselect
from lxml import html, etree
from bergamot.config import repository
import typing as t


def convert(node):
    return etree.tostring(node, method="html", encoding="utf-8").decode("utf-8")


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
                    bergamot.VectorString([convert(tree)]),
                    options,
                )
            else:
                forward_model = self.get_model(model)
                [response] = self.service.translate(
                    forward_model, bergamot.VectorString([convert(tree)]), options
                )

            return self.postprocess(response.target.text)

    def get_model(self, code):
        if code not in self.cache:
            config = repository.modelConfigPath(code)
            self.cache[code] = self.service.modelFromConfigPath(config)
        return self.cache[code]

    def postprocess(self, text):
        return text
