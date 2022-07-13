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
    return {key: (value, new_dict[key]) for key, value in old_dict.items() if key in new_dict and new_dict[key] != value}

def main():
    args = iter(sys.argv[1:])
    errors = {}
    duplicate_ids = []
    
    if args:
        for arg in args:
            changed_ids = find_changed_ids(arg, next(args))
            for id, value in changed_ids.items():
                if id in errors:
                    duplicate_ids.append((id))
                else:
                    errors[id] = value
    
    if errors:
        ids = list(errors.keys())
        ids.sort()

        output = []
        total_errors = 0
        for id in ids:
            print(errors[id])
            output.append(
                f"\nID: {id}"
                f"\nBefore: {errors[id][0]}"
                f"\nAfter: {errors[id][1]}"
                )
            total_errors+= 1
        output.append(f"\nTotal errors: {total_errors}")

        if duplicate_ids:
            output.append(f"\nDuplicate IDs found:")
            for id in duplicate_ids:
                output.append(f"\nID: {id}")                

        print("\n".join(output))
        sys.exit(1)
    else:
        print("No unchanged IDs found.")

if __name__ == "__main__":
    main()
