#!/usr/bin/env python3
import argparse
import os
import sys
from glob import glob
from compare_locales.parser import getParser
from compare_locales.serializer import serialize


def main():
    '''Checks if a string ID exists in a file for all locales'''

    arguments = argparse.ArgumentParser()
    arguments.add_argument(
        "--dir",
        required=True,
        dest="base_folder",
        help="Path to folder containing locale data",
    )
    arguments.add_argument(
        "--files",
        nargs="*",
        required=True,
        dest="filenames",
        help="Filename to check",
    )
    arguments.add_argument(
        "--string",
        nargs="*",
        required=True,
        dest="string_ids",
        help="String ids to find",
    )

    args = arguments.parse_args()

    # Get a list of files to update (absolute paths)
    base_folder = os.path.realpath(args.base_folder)
    locales = [
    d
    for d in os.listdir(base_folder)
    if os.path.isdir(os.path.join(base_folder, d)) and not d.startswith(".")
        ]
    output = {}
    for locale in locales:
        output[locale] = []
        for filename in args.filenames:
            target_file_path = os.path.join(base_folder, locale, filename)
            target_parser = getParser(target_file_path)
            try:
                target_parser.readFile(target_file_path)
            except FileNotFoundError:
                continue
            targets = [
                entity
                for entity in list(target_parser.walk(only_localizable=True))
                if f"{entity}" in args.string_ids
            ]
            for target in targets:
                output[locale].append(f"{filename}")
                output[locale].append(f"{target} = {target.raw_val}")
                output[locale].append("")
        
    for key, value in sorted(output.items()):
        if value:
            print(key)
            for item in value:
                print(item)

if __name__ == "__main__":
    main()
