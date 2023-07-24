#! /usr/bin/env python

import argparse
from pathlib import Path
import tinify


tinify.key = ""


def main():
    # Parse command line options
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        help="Path to folder with PNG files to optimize (recursive)",
        required=True,
    )
    parser.add_argument(
        "--key",
        help="API Key",
        required=True,
    )
    args = parser.parse_args()

    tinify.key = args.key

    src_path = Path(args.path)
    file_paths = [p for p in src_path.rglob("**/*.png")]

    for image in file_paths:
        # Optimize image
        try:
            print(f"Optimizing image: {image}")
            source = tinify.from_file(image)
            source.to_file(image)
        except Exception as e:
            print(e)
            print(f"Error optimizing image: {image}")


if __name__ == "__main__":
    main()
