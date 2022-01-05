import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import cssselect
from lxml import html, etree


def convert(node):
    return etree.tostring(node, method="html", encoding="utf-8").decode("utf-8")


class HTMLTranslator:
    def __init__(self, model_config, num_workers, cache_size, cache_mutex_buckets):
        # TODO(jerinphilip): Improve syntax upstream.
        config = ServiceConfig(
            numWorkers=num_workers,
            cacheSize=cache_size,
            cacheMutexBuckets=cache_mutex_buckets,
        )

        self.service = Service(config)

        # What model are we using?
        self.model = self.service.modelFromConfigPath(model_config)

    def translate(self, page: str, bypass: bool = False):
        # Hardcode a bunch of options for now. TODO: improve
        options = ResponseOptions(HTML=True)

        # Get nodes. Replace them in place.
        tree = html.fromstring(page)

        for node in tree.iterdescendants():
            if node.text is None:
                node.text = ""

        imgs = tree.xpath("/html//img")
        print("Images to begin with", len(imgs))

        if bypass:
            return self.postprocess(convert(tree))
        else:
            [response] = self.service.translate(
                self.model, bergamot.VectorString([convert(tree)]), options
            )
            return self.postprocess(response.target.text)

    def postprocess(self, text):
        node = html.fromstring(text)
        imgs = node.xpath("//img")
        print("Images at translated", len(imgs))
        return response.target.text
