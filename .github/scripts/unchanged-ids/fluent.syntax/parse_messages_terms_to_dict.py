import argparse
from fluent.syntax import parse, ast
from fluent.syntax.serializer_value import FluentSerializerValue

parser = argparse.ArgumentParser()
parser.add_argument("old")
parser.add_argument("new")
args = parser.parse_args()

serializer = FluentSerializerValue()

def generate_dict_from_file(file):
    fn = open(file)
    resource = parse(fn.read())
    fn.close()
    return {entry.id.name: serializer.serialize_entry(entry) for entry in resource.body if isinstance(entry, ast.Message) or isinstance(entry, ast.Term)}

def find_changed_ids(file_old, file_new):
    old_dict = generate_dict_from_file(file_old)
    new_dict = generate_dict_from_file(file_new)
    return {key: {value, new_dict[key]} for key, value in old_dict.items() if key in new_dict and new_dict[key] != value}

def main():
    file_old = args.old
    file_new = args.new

    changed_ids = find_changed_ids(file_old, file_new)

    for key, value in changed_ids.items():
        print(key, value)

if __name__ == "__main__":
    main()
