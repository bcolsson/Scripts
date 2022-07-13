import argparse
import sys
from fluent.syntax import parse, ast
from fluent.syntax.serializer_value import FluentSerializerValue

serializer = FluentSerializerValue()

def generate_dict_from_file(file):
    try:
        with open(file) as f:
            resource = parse(f.read())
            return {entry.id.name: serializer.serialize_entry(entry) for entry in resource.body if isinstance(entry, ast.Message) or isinstance(entry, ast.Term)}
        except Exception as e:
            sys.exit(e)

def find_changed_ids(file_old, file_new):
    old_dict = generate_dict_from_file(file_old)
    new_dict = generate_dict_from_file(file_new)
    return {key: {value, new_dict[key]} for key, value in old_dict.items() if key in new_dict and new_dict[key] != value}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("old")
    parser.add_argument("new")
    args = parser.parse_args()

    file_old = args.old
    file_new = args.new

    changed_ids = find_changed_ids(file_old, file_new)

    for key, value in changed_ids.items():
        print(key, value)

if __name__ == "__main__":
    main()
