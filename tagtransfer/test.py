import yaml
import os
import argparse
import sys
from collections import Counter
from collections import defaultdict

import bergamot
from bergamot import Service, Response, ResponseOptions, ServiceConfig, TranslationModel



if __name__ == '__main__':
    config = ServiceConfig()
    config.numWorkers = 4;
    config.cacheSize = 2000;
    config.cacheMutexBuckets = 18;
    service = Service(config);

    options = ResponseOptions();
    options.alignment = True
    options.qualityScores = True
    options.HTML = True

    configPath = "/home/jerin/.local/share/lemonade/models/ende.student.tiny11/config.bergamot.yml"
    model = service.modelFromConfigPath(configPath)

    from .examples import EXAMPLES

    for example in EXAMPLES:
        try:
            samples = bergamot.VectorString([example["input"]])
            responses = service.translate(model, samples, options)
            response = responses[0]
            print('[src] > ', response.source.text)
            print('[hyp] > ', response.target.text)
            print('[tgt] > ', example["expectedProjectedString"])
            print()
        except:
            print("Failure on: ", example["input"], file=sys.stderr)
            pass

