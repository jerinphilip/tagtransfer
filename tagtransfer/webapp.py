from flask import Flask
from flask import request
from lxml import html, etree
import requests
from .html_translator import (
    HTMLTranslator,
    make_soup,
    soup_relaxed,
)
import argparse
import urllib
import tidylib

# from html import unescape
# import re

app = Flask(__name__)
translator = None


@app.route("/")
def index():
    url = request.args.get("url", "https://en.wikipedia.org/wiki/Physics")
    bypass = request.args.get("bypass", "false").lower() == "true"
    model1 = request.args.get("model", "en-de-tiny")
    model2 = request.args.get("pivot", None)
    translated = translator.translate_url(model1, model2, url, bypass)

    base_url = request.base_url

    def transform_url(u):
        u = urllib.parse.urljoin(url, u)
        params = {
            "url": u,
            "model": model1,
            "bypass": str(bypass).lower(),
            "bypass": bypass,
        }

        if model2 is not None:
            params["pivot"] = model2

        paramstring = urllib.parse.urlencode(params)
        return f"{base_url}/?{paramstring}"

    # I only need minimum clickable links transferred, so going for <a>.
    # <button> etc are ignored.
    soup = make_soup(translated)
    for a in soup.find_all("a"):
        href = a.get("href", False)
        if href:
            if href[0] == "#":
                # This block circumvent base href prepending urls affecting
                # in-page navigation by means of javascript.
                a["href"] = "javascript:;"
                a["onclick"] = "document.location.hash='{}'".format(href.lstrip("#"))
            else:
                a["href"] = transform_url(href)

    return soup_relaxed(soup)


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
