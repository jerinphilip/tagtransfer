from .html_translator import HTMLTranslator
import requests
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, required=True)
    parser.add_argument(
        "--model-config",
        type=str,
        help="Path to model file to use in tag-transfer translation",
        required=True,
    )
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
    parser.add_argument(
        "--cache-mutex-buckets",
        type=int,
        help="How many mutex buckets to use to reduce contention in cache among workers.",
        default=20,
    )

    args = parser.parse_args()
    response = requests.get(args.url)

    translator = HTMLTranslator(
        args.model_config, args.num_workers, args.cache_size, args.cache_mutex_buckets
    )
    document = translator.translate(response.text)
    print(document)
