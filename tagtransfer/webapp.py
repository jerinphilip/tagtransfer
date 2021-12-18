from flask import Flask
from flask import request
from lxml import html, etree
import requests
from .html_translator import HTMLTranslator, BASE_OPTIONS
import argparse
import tidylib

app = Flask(__name__)
translator = None

@app.route("/")
def hello_world():
    url = request.args.get("url", "https://en.wikipedia.org/wiki/Physics")
    response = requests.get(url)
    document = translator.translate(response.text)
    tree = html.fromstring(document)
    head = tree.xpath('/html/head')[0]
    head.insert(1, html.fragment_fromstring('<base href="{}" target="_blank">'.format(url)))
    document, errors = tidylib.tidy_document(etree.tostring(tree).decode("utf-8"), BASE_OPTIONS)
    return document


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-config', type=str, help="Path to model file to use in tag-transfer translation", required=True)
    parser.add_argument('--num-workers', type=int, help="Number of worker threads to use to translate", default=1)
    parser.add_argument('--cache-size', type=int, help="How many sentences to hold in cache", default=2000)
    parser.add_argument('--cache-mutex-buckets', type=int, help="How many mutex buckets to use to reduce contention in cache among workers.", default=20)

    args = parser.parse_args()
    translator = HTMLTranslator(args.model_config, args.num_workers, args.cache_size, args.cache_mutex_buckets)

    app.run('0.0.0.0', '8080')
