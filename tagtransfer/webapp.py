from flask import Flask
from flask import request
from lxml import html, etree
import requests
from .html_translator import HTMLTranslator
import argparse

# from html import unescape
# import re

app = Flask(__name__)
translator = None


@app.route("/")
def index():
    url = request.args.get("url", "https://en.wikipedia.org/wiki/Physics")
    bypass = request.args.get("bypass", "false") == "true"
    model1 = request.args.get("model", "en-de-tiny")
    model2 = request.args.get("pivot", None)
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
        1, html.fragment_fromstring('<base href="{}" target="_blank">'.format(url))
    )

    # Translate document HTML
    translated = translator.translate(
        model1,
        model2,
        etree.tostring(
            tree, method="html", pretty_print=True, encoding="utf-8"
        ).decode(),
        bypass,
    )

    return f"<!DOCTYPE html>\n{translated}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-workers",
        type=int,
        help="Number of worker threads to use to translate",
        default=1,
    )
    parser.add_argument(
        "--cache-size",
        type=int,
        help="How many sentences to hold in cache",
        default=2000,
    )

    args = parser.parse_args()
    translator = HTMLTranslator(args.num_workers, args.cache_size)
    app.run("0.0.0.0", "8080")
