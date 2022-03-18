import argparse
import json
import os
import sys
import typing as t
from collections import defaultdict, namedtuple

import bergamot
import sacrebleu
from bergamot import (
    REPOSITORY,
    Response,
    ResponseOptions,
    Service,
    ServiceConfig,
    TranslationModel,
)
from lxml import etree

SACREBLEU_METRIC = "bleu"


class MarkedUpPair:
    """
    namedtuple is not editable after creation, so we have this record type.
    This is used in Dataset below to create pairs of entries for markup-translation.
    """

    def __init__(self, _id, source, target=None):
        self.id = _id
        self.source = source
        self.target = target

    def __repr__(self):
        """Convenience repr function"""
        return {"id": self.id, "source": self.source, "target": self.target}.__repr__()


class Dataset:
    """A Dataset, similar to torch.Dataset"""

    def __init__(
        self, source_path, target_path, strict_markup=False, filter_fn=lambda x: True
    ):

        # Salesforce dataset is json.
        source_json = self._load_json(source_path)
        target_json = self._load_json(target_path)
        self._data = {}

        for key, value in source_json.items():
            self._data[key] = MarkedUpPair(key, value)

        for key, value in target_json.items():
            self._data[key].target = value
            assert self._data[key].id == key

        self._sorted_keys = [
            key for key in sorted(self._data.keys()) if filter_fn(self._data[key])
        ]

    def __getitem__(self, idx):
        return self._data[self._sorted_keys[idx]]

    def __len__(self):
        return len(self._sorted_keys)

    def _load_json(self, json_path):
        with open(json_path) as fp:
            data = json.load(fp)
            text = data["text"]
            return text


def wrapGenXML(content):
    # The text as provided by salesforce contains tags but is not valid
    # xml, we wrap around a root to get lxml parsing superpowers.
    xml_value = "<root>{}</root>".format(content)
    node = etree.fromstring(xml_value)
    return node


def stringify_children(content):
    """
    Utility function to strip xml/html tags from an etree node. Used when
    disabled HTML translation to isolate errors to HTML pipeline or no-HTML
    pipeline.
    """
    return "".join(wrapGenXML(content).itertext())


def matchXML(hypothesis: etree._Element, gold: etree._Element):
    """
    Try to match tree structure with gold translation with tags. This is a
    binary value, and works only if strongly matches.

    Taken from https://github.com/salesforce/localization-xml-mt/blob/master/scripts/evaluate.py
    """
    if hypothesis.tag != gold.tag:
        return False

    hypothesis = list(hypothesis.iterchildren())
    gold = list(gold.iterchildren())

    if len(hypothesis) != len(gold):
        return False

    for (h, g) in zip(hypothesis, gold):
        if not matchXML(h, g):
            return False

    return True


def add_sacreblue_dummy_args(parser):
    # BLEU related arguments: These are required to use sacreBleu
    parser.add_argument(
        "--smooth-method",
        "-s",
        choices=sacrebleu.metrics.METRICS[SACREBLEU_METRIC].SMOOTH_DEFAULTS.keys(),
        default="exp",
        help="smoothing method: exponential decay (default), floor (increment zero counts), add-k (increment num/denom by k for n>1), or none",
    )
    parser.add_argument(
        "--smooth-value",
        "-sv",
        type=float,
        default=None,
        help="The value to pass to the smoothing technique, only used for floor and add-k. Default floor: {}, add-k: {}.".format(
            sacrebleu.metrics.METRICS[SACREBLEU_METRIC].SMOOTH_DEFAULTS["floor"],
            sacrebleu.metrics.METRICS[SACREBLEU_METRIC].SMOOTH_DEFAULTS["add-k"],
        ),
    )
    parser.add_argument(
        "--tokenize",
        "-tok",
        choices=sacrebleu.tokenizers.TOKENIZERS.keys(),
        default="13a",
        help="Tokenization method to use for BLEU. If not provided, defaults to `zh` for Chinese, `mecab` for Japanese and `mteval-v13a` otherwise.",
    )
    parser.add_argument(
        "-lc",
        action="store_true",
        default=False,
        help="Use case-insensitive BLEU (default: False)",
    )
    parser.add_argument(
        "--force",
        default=False,
        action="store_true",
        help="insist that your tokenized input is actually detokenized",
    )


if __name__ == "__main__":
    # Setup a parser.
    parser = argparse.ArgumentParser("Load a dataset, run tag transfer using bergamot")
    parser.add_argument(
        "--dataset-dir",
        type=str,
        help="Path to extracted folder containing json data",
        required=True,
    )

    parser.add_argument("--split", type=str, choices=["train", "dev"], default="dev")

    parser.add_argument(
        "--num-workers",
        type=int,
        help="Number of worker threads to use to translate",
        default=4,
    )
    parser.add_argument(
        "--cache-size",
        type=int,
        help="How many sentences to hold in cache",
        default=2000,
    )
    parser.add_argument(
        "--disable-markup-in-translation",
        action="store_true",
        help="Disable markup pipeline. Useful in diagnosing if things work without markup.",
    )

    parser.add_argument(
        "--include-non-markup",
        action="store_true",
        help="Only feed entries containing markup to the pipeline.",
    )

    parser.add_argument(
        "--log-level", type=str, default="off", help="Bergamot log level"
    )

    langpair_to_models = {
        "enfi": ("opus", "eng-fin-tiny"),
        "ende": ("browsermt", "en-de-tiny"),
    }

    parser.add_argument(
        "--langpair",
        type=str,
        required=True,
        help="lang-pair to use",
        choices=langpair_to_models.keys(),
    )

    add_sacreblue_dummy_args(parser)
    args = parser.parse_args()

    metric = sacrebleu.metrics.METRICS[SACREBLEU_METRIC](args)

    config = ServiceConfig(
        numWorkers=args.num_workers, cacheSize=args.cache_size, logLevel=args.log_level
    )
    service = Service(config)

    # What model are we using?
    repository, model_name = langpair_to_models[args.langpair]
    modelConfigPath = REPOSITORY.modelConfigPath(repository, model_name)
    model = service.modelFromConfigPath(modelConfigPath)

    options = ResponseOptions(
        alignment=True, HTML=not args.disable_markup_in_translation
    )

    def filter_fn(pair):
        # Only if the actual text contains tags, need we bother.
        tree = wrapGenXML(pair.source)
        child_count = len(tree.xpath(".//*"))
        return child_count > 0

    src_lang, tgt_lang = args.langpair[:2], args.langpair[2:]
    dataset = Dataset(
        source_path=os.path.join(
            args.dataset_dir,
            f"{args.langpair}/{args.langpair}_{src_lang}_{args.split}.json",
        ),
        target_path=os.path.join(
            args.dataset_dir,
            f"{args.langpair}/{args.langpair}_{tgt_lang}_{args.split}.json",
        ),
        filter_fn=filter_fn if not args.include_non_markup else lambda x: True,
    )

    source_texts = []
    for idx in range(len(dataset)):
        pair = dataset[idx]
        source_texts.append(pair.source)

    responses = service.translate(model, bergamot.VectorString(source_texts), options)

    # Produce metrics.
    accuracy_stats = defaultdict(int)

    with_tags = {"hypotheses": [], "references": [[]]}
    without_tags = {"hypotheses": [], "references": [[]]}

    for idx in range(len(dataset)):
        pair = dataset[idx]
        response = responses[idx]
        isMatch = matchXML(wrapGenXML(pair.target), wrapGenXML(response.target.text))

        print("[src] > ", response.source.text)
        print("[hyp] > ", response.target.text)
        print("[tgt] > ", pair.target)
        bleu_with_tags = metric.sentence_score(response.target.text, [pair.target])
        bleu_without_tags = metric.sentence_score(
            stringify_children(response.target.text), [stringify_children(pair.target)]
        )
        print("With tags: ", bleu_with_tags)
        print("Without tags: ", bleu_without_tags)
        print("Target structures (HTML) match perfectly? ", "Yes" if isMatch else "No")
        print()

        with_tags["hypotheses"].append(response.target.text)
        with_tags["references"][0].append(pair.target)

        without_tags["hypotheses"].append(stringify_children(response.target.text))
        without_tags["references"][0].append(stringify_children(pair.target))

        accuracy_stats["correct"] += int(isMatch)
        accuracy_stats["wrong"] += int(not isMatch)

    accuracy = accuracy_stats["correct"] / (
        accuracy_stats["correct"] + accuracy_stats["wrong"]
    )

    with_tags_bleu = metric.corpus_score(
        with_tags["hypotheses"], with_tags["references"]
    )

    without_tags_bleu = metric.corpus_score(
        without_tags["hypotheses"], without_tags["references"]
    )

    print("Total XML accuracy: {:.2f}%".format(accuracy * 100))
    print("Without tags corpus BLEU: {}".format(without_tags_bleu))
    print("With tags corpus BLEU: {}".format(with_tags_bleu))
