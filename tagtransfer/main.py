import json
from argparse import ArgumentParser
from lxml import etree
from collections import defaultdict, namedtuple
import sys

import pybergamot
from pybergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel

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
        """ Convenience repr function """
        return {'id': self.id, 'source': self.source, 'target': self.target}.__repr__()

class Dataset:
    """ A Dataset, similar to torch.Dataset """
    def __init__(self, source_path, target_path, strict_markup=False, filter_fn = lambda x: True):

        # Salesforce dataset is json.
        source_json = self._load_json(source_path)
        target_json = self._load_json(target_path)
        self._data = {}

        for key, value in source_json.items():
            self._data[key] = MarkedUpPair(key, value)

        for key, value in target_json.items():
            self._data[key].target = value
            assert(self._data[key].id == key)

        self._sorted_keys = [ key for key in sorted(self._data.keys()) if filter_fn(self._data[key]) ]

    def __getitem__(self, idx):
        return self._data[self._sorted_keys[idx]]

    def __len__(self):
        return len(self._sorted_keys)

    def _load_json(self, json_path):
        with open(json_path) as fp:
            data = json.load(fp)
            text = data["text"]
            return text

def stringify_children(content):
    """ 
    Utility function to strip xml/html tags from an etree node. Used when
    disabled HTML translation to isolate errors to HTML pipeline or no-HTML
    pipeline.
    """
    xml_value = '<root> {} </root>'.format(content)
    node = etree.fromstring(xml_value)
    return ''.join(node.itertext())

if __name__ == '__main__':
    # Setup a parser.
    parser = ArgumentParser("Load a dataset, run tag transfer using bergamot")
    parser.add_argument('--source-data', type=str, help="Path to json file from localization-xml-mt (salesforce)", required=True)
    parser.add_argument('--target-data', type=str, help="Path to json file from localization-xml-mt (salesforce)", required=True)
    parser.add_argument('--model-config', type=str, help="Path to model file to use in tag-transfer translation", required=True)
    parser.add_argument('--num-workers', type=int, help="Number of worker threads to use to translate", default=4)
    parser.add_argument('--cache-size', type=int, help="How many sentences to hold in cache", default=2000)
    parser.add_argument('--cache-mutex-buckets', type=int, help="How many mutex buckets to use to reduce contention in cache among workers.", default=20)
    parser.add_argument('--disable-markup-in-translation', action='store_true', help="Disable markup pipeline. Useful in diagnosing if things work without markup.")
    parser.add_argument('--include-non-markup', action='store_true', help="Only feed entries containing markup to the pipeline.")

    args = parser.parse_args()

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
    options.HTML = not args.disable_markup_in_translation

    def filter_fn(pair):
        # The text as provided by salesforce contains tags but is not valid
        # xml, we wrap around a root to get lxml parsing superpowers.
        # Only if the actual text contains tags, need we bother.
        xml_value = '<root> {} </root>'.format(pair.source)
        tree = etree.fromstring(xml_value)
        child_count = len(tree.xpath(".//*"))
        return child_count > 0

    dataset = Dataset(args.source_data, args.target_data, filter_fn = filter_fn if not args.include_non_markup else lambda x: True)

    source_texts = []
    for idx in range(len(dataset)):
        pair = dataset[idx]
        source_texts.append(pair.source)

    responses = service.translate(model, pybergamot.VectorString(source_texts), options)

    for idx in range(len(dataset)):
        pair = dataset[idx]
        response = responses[idx]
        print('[src] > ', response.source.text)
        print('[hyp] > ', response.target.text)
        print('[tgt] > ', pair.target)
        print()


