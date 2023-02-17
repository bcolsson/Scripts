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
        "--ignore-locale",
        nargs="*",
        required=False,
        dest="ignore_locales",
        help="Ignore locales",
    )
    arguments.add_argument(
        "--omit-id",
        nargs="*",
        required=False,
        dest="omit_ids",
        help="Omit ids",
    )
    arguments.add_argument(
        "--path",
        required=True,
        dest="base_folder",
        help="Path to folder including subfolders for all locales.",
    )
    arguments.add_argument(
        "--migrate",
        required=False,
        default="*.ftl",
        dest="migrate_filename",
        help="Filename. Indicates the file that will be generated and the source of string ids that will be added if translations exist. By default translations will be pulled from the locale version unless --translations is used.",
    )
    arguments.add_argument(
        "--translations",
        required=False,
        dest="translations_filename",
        help="Alternate source of translations if migrating translations from a different file into the file for --migrate.",
    )
    arguments.add_argument(
        "--merge",
        action="store_true",
        dest="merge",
        help="Merge into an existing file. Note: Uses values from the existing file if there are duplicate IDs. ",
    )
    arguments.add_argument("locales", nargs="*", help="Locales to process")

    args = arguments.parse_args()
    if args.translations_filename and args.migrate_filename is None:
        arguments.error("--target requires --source.")
    if args.merge and args.translations_filename is None:
        arguments.error("--merge requires --target.")
    omit_ids = []
    if args.omit_ids:
        omit_ids = [id.lstrip() for id in args.omit_ids]
    reference_locale = args.reference_locale

    # Get a list of files to update (absolute paths)
    base_folder = os.path.realpath(args.base_folder)
    reference_path = os.path.join(base_folder, reference_locale)

    reference_files = []
    for ftl_path in glob(
        reference_path + f"/**/{args.migrate_filename}", recursive=True
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
            translations_filename = filename
            if args.translations_filename:
                translations_filename = filename.replace(
                    args.migrate_filename, args.translations_filename
                )
            target_file_path = os.path.join(base_folder, locale, translations_filename)
            output_file_path = os.path.join(base_folder, locale, filename)
            target_parser = getParser(target_file_path)
            target_parser.readFile(target_file_path)

            output = []
            target = [
                entity
                for entity in list(target_parser.walk(only_localizable=True))
                if f"{entity}" not in omit_ids
            ]
            if args.merge:
                merged_file_parser = getParser(output_file_path)
                merged_file_parser.readFile(output_file_path)
                output = [
                    entity
                    for entity in list(merged_file_parser.walk(only_localizable=True))
                    if f"{entity}" not in omit_ids
                ]
                # Read values from existing file, preserves entities from existing file and ignores duplicates in target file.
                output_strings = [f"{entity}" for entity in output]
                for target_entity in target:
                    if f"{target_entity}" in output_strings:
                        continue
                    output.append(target_entity)
            else:
                output.extend(target)

            output_data = serialize(filename, reference, output, {})

            print(f"Writing {output_file_path}")
            with open(output_file_path, "wb") as f:
                f.write(output_data)


if __name__ == "__main__":
    main()
