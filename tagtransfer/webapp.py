from flask import Flask
from flask import request
from lxml import html, etree
import requests
from .html_translator import HTMLTranslator
import argparse
import urllib

# from html import unescape
# import re

app = Flask(__name__)
translator = None


@app.route("/")
def index():
    url = request.args.get("url", "https://en.wikipedia.org/wiki/Physics")
    bypass = request.args.get("bypass", "false").lower() == "true"
    model1 = request.args.get("model", "en-de-tiny")
    use_tidy = request.args.get("use_tidy", "false").lower() == "true"
    model2 = request.args.get("pivot", None)
    translated = translator.translate_url(model1, model2, url, bypass, use_tidy)

    base_url = request.base_url

    def transform_url(u):
        u = urllib.parse.urljoin(url, u)
        params = {
            "url": u,
            "model": model1,
            "bypass": str(bypass).lower(),
            "use_tidy": use_tidy,
        }

        if model2 is not None:
            params["pivot"] = model2

        paramstring = urllib.parse.urlencode(params, safe=":/")
        return f"{base_url}/?{paramstring}"

    # I only need minimum clickable links transferred, so going for <a>.
    # <button> etc are ignored.
    tree = html.fromstring(translated)
    anchors = tree.xpath("//a")
    for anchor in anchors:
        href = anchor.attrib.get("href", None)
        if href:
            if href[0] == "#":
                # This block circumvent base href prepending urls affecting
                # in-page navigation by means of javascript.
                anchor.attrib["href"] = "javascript:;"
                anchor.attrib["onclick"] = "document.location.hash='{}'".format(
                    href.lstrip("#")
                )
            else:
                anchor.attrib["href"] = transform_url(href)

    return etree.tostring(tree, method="html", encoding="utf-8").decode("utf-8")


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

    parser.add_argument("--port", type=int, help="Port to run server on", default=8080)

    args = parser.parse_args()
    translator = HTMLTranslator(args.num_workers, args.cache_size)
    app.run("0.0.0.0", args.port, debug=True)
