import json
from argparse import ArgumentParser
from lxml import etree
from .pybergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel
from collections import defaultdict, namedtuple


class MarkedUpPair:
    def __init__(self, _id, source, target=None):
        self.id = _id
        self.source = source
        self.target = target

    def __repr__(self):
        return {'id': self.id, 'source': self.source, 'target': self.target}.__repr__()

class Dataset:
    """ A Dataset, similar to torch.Dataset """
    def __init__(self, source_path, target_path, strict_markup=False):
        source_json = self._load_json(source_path)
        target_json = self._load_json(target_path)
        self._data = {}

        for key, value in source_json.items():
            self._data[key] = MarkedUpPair(key, value)

        for key, value in target_json.items():
            self._data[key].target = value
            assert(self._data[key].id == key)

        self._sorted_keys = sorted(self._data.keys())

    def __getitem__(self, idx):
        return self._data[self._sorted_keys[idx]]

    def __len__(self):
        return len(self._data)

    def _load_json(self, json_path):
        with open(json_path) as fp:
            data = json.load(fp)
            text = data["text"]
            return text


if __name__ == '__main__':
    # Setup a parser.
    parser = ArgumentParser("Load a dataset, run tag transfer using bergamot")
    parser.add_argument('--source-data', type=str, help="Path to json file from localization-xml-mt (salesforce)", required=True)
    parser.add_argument('--target-data', type=str, help="Path to json file from localization-xml-mt (salesforce)", required=True)
    parser.add_argument('--model-config', type=str, help="Path to model file to use in tag-transfer translation", required=True)
    parser.add_argument('--num-workers', type=int, help="Number of worker threads to use to translate", default=4)
    parser.add_argument('--cache-size', type=int, help="How many sentences to hold in cache", default=2000)
    parser.add_argument('--cache-mutex-buckets', type=int, help="How many mutex buckets to use to reduce contention in cache among workers", default=20)

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
    options.HTML = True


    dataset = Dataset(args.source_data, args.target_data)
    for idx in range(len(dataset)):
        pair = dataset[idx]
        # The text is not valid xml, we wrap around a root to get lxml parsing superpowers.
        xml_value = '<root> {} </root>'.format(pair.source)
        tree = etree.fromstring(xml_value)
        child_count = len(tree.xpath(".//*"))

        # Only if the actual text contains tags, need we bother.
        if child_count > 0:
            try:
                response = service.translate(model, pair.source, options)
                print('[src] > ', response.source.text)
                print('[hyp] > ', response.target.text)
                print('[tgt] > ', pair.target)
                print()
            except:
                print("Failure on: ", value, file=sys.stderr)
                pass


