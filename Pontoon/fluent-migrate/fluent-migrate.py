#!/usr/bin/env python3
import argparse
import os
import sys
from glob import glob
from compare_locales.parser import getParser
from compare_locales.serializer import serialize


def main():
    arguments = argparse.ArgumentParser()
    arguments.add_argument(
        "--reference",
        required=True,
        dest="reference_locale",
        help="Reference locale code",
    )
    arguments.add_argument(
        "--ignore",
        nargs="*",
        required=False,
        dest="ignore_locales",
        help="Ignore locales",
    )
    arguments.add_argument(
        "--path",
        required=True,
        dest="base_folder",
        help="Path to folder including subfolders for all locales",
    )
    arguments.add_argument(
        "--source",
        required=False,
        default="*.ftl",
        dest="source_filename",
        help="Name of source language file",
    )
    arguments.add_argument(
        "--target",
        required=False,
        dest="target_filename",
        help="Name of target language file",
    )
    arguments.add_argument(
        "--merge",
        action="store_true",
        dest="merge",
        help="Merge into an existing file",
    )
    arguments.add_argument("locales", nargs="*", help="Locales to process")

    args = arguments.parse_args()
    if args.target_filename and args.source_filename is None:
        arguments.error("--target requires --source.")
    if args.merge and args.target_filename is None:
        arguments.error("--merge requires --target.")

    reference_locale = args.reference_locale

    # Get a list of files to update (absolute paths)
    base_folder = os.path.realpath(args.base_folder)
    reference_path = os.path.join(base_folder, reference_locale)

    reference_files = []
    for ftl_path in glob(
        reference_path + f"/**/{args.source_filename}", recursive=True
    ):
        reference_files.append(os.path.relpath(ftl_path, reference_path))
    if not reference_files:
        sys.exit(
            f"No reference file found in {os.path.join(base_folder, reference_locale)}"
        )

    # Get the list of locales
    if args.locales:
        locales = args.locales
    else:
        locales = [
            d
            for d in os.listdir(base_folder)
            if os.path.isdir(os.path.join(base_folder, d)) and not d.startswith(".")
        ]
        locales.remove(reference_locale)
        if args.ignore_locales:
            for locale in args.ignore_locales:
                locales.remove(locale)
        locales.sort()

    for filename in reference_files:
        try:
            reference_file_path = os.path.join(base_folder, reference_locale, filename)
            source_parser = getParser(reference_file_path)
            source_parser.readFile(reference_file_path)
            reference = list(source_parser.walk())
        except Exception as e:
            sys.exit(f"ERROR: Can't parse reference file {filename}\n{e}")

        for locale in locales:
            target_filename = filename
            if args.target_filename:
                target_filename = filename.replace(
                    args.source_filename, args.target_filename
                )
            target_file_path = os.path.join(base_folder, locale, target_filename)
            output_file_path = os.path.join(base_folder, locale, filename)
            if args.merge:
                with open(output_file_path, "a") as modified_file:
                    with open(target_file_path) as merged_file:
                        modified_file.write(merged_file.read())
                target_file_path = output_file_path

            target_parser = getParser(target_file_path)
            target_parser.readFile(target_file_path)
            target = list(target_parser.walk(only_localizable=True))

            output = serialize(filename, reference, target, {})

            print(f"Writing {output_file_path}")
            with open(output_file_path, "wb") as f:
                f.write(output)


if __name__ == "__main__":
    main()
