import requests
import lxml
from lxml import html, etree
import tidylib
from lxml.html import xhtml_to_html
import argparse
import cssselect
import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
import sys

def print_node(x):
    fragment = etree.tostring(x, pretty_print=True)
    print(fragment)

def convert_legal(x):
    fragment = html.fromstring(x)
    document, errors = tidylib.tidy_fragment(etree.tostring(fragment, method='html', pretty_print=True))
    return document


def batched(service, model, inners):
    try:
        responses = service.translate(model, bergamot.VectorString(inners), options)
        for response in responses:
            try:
                source = html.fromstring(response.source.text)
                print("Source: ", "-"*30)
                print_node(source)
                if response.target.text:
                    print("Target: ", "-"*30)
                    target = html.fromstring(response.target.text)
                    print(target)
                print()
            except:
                print("Failure on", file=sys.stderr)
                print(response.source.text, file=sys.stderr)
                print(response.target.text, file=sys.stderr)
                raise
    except:
        print("Failure on", inners, file=sys.stderr)
        raise

def single_sample(service, model, inners):
    for inner in inners:
        # print(inner)
        try:
            responses = service.translate(model, bergamot.VectorString([inner]), options)
            for response in responses:
                try:
                    source = html.fromstring(response.source.text)
                    #print("Source: ", "-"*30)
                    # print_node(source)
                    if response.target.text:
                        # print("Target: ", "-"*30)
                        target = html.fromstring(response.target.text)
                        document, errors = tidylib.tidy_fragment(response.target.text)
                        print(document)
                    print()
                except:
                    print("Failure on", file=sys.stderr)
                    print(response.source.text, file=sys.stderr)
                    print(response.target.text, file=sys.stderr)
                    raise
        except:
            print("Failure on", inner, file=sys.stderr)
            raise




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--model-config', type=str, help="Path to model file to use in tag-transfer translation", required=True)
    parser.add_argument('--num-workers', type=int, help="Number of worker threads to use to translate", default=1)
    parser.add_argument('--cache-size', type=int, help="How many sentences to hold in cache", default=2000)
    parser.add_argument('--cache-mutex-buckets', type=int, help="How many mutex buckets to use to reduce contention in cache among workers.", default=20)
    parser.add_argument('--tag', type=str, help="Tag to check if translates", default='p')

    args = parser.parse_args()
    response = requests.get(args.url)

    BASE_OPTIONS = {
      "indent": 1,           # Pretty; not too much of a performance hit
      "tidy-mark": 0,        # No tidy meta tag in output
      "wrap": 0,             # No wrapping
      "alt-text": "",        # Help ensure validation
      "doctype": 'strict',   # Little sense in transitional for tool-generated markup...
      "force-output": 1,     # May not get what you expect but you will get something
      "output-html": 1,
    }


    # Use tidylib first round.
    document, errors = tidylib.tidy_document(response.text, BASE_OPTIONS)
    # print(errors)

    tree = html.fromstring(document)

    # TODO(jerinphilip): Improve syntax upstream.
    config = ServiceConfig()
    config.numWorkers = args.num_workers;
    config.cacheSize = args.cache_size;
    config.cacheMutexBuckets = args.cache_mutex_buckets;

    service = Service(config)


    # What model are we using?
    model = service.modelFromConfigPath(args.model_config)

    # Hardcode a bunch of options for now. TODO: improve
    options = ResponseOptions();
    options.alignment = True
    options.qualityScores = True
    options.HTML = True

    paragraphs = tree.cssselect(args.tag)

    source_texts = [] 
    for paragraph in paragraphs:
        fragment = etree.tostring(paragraph, pretty_print=True)
        if fragment:
            source_texts.append(fragment)

    inners = list(map(convert_legal, source_texts))
    single_sample(service, model, inners)





