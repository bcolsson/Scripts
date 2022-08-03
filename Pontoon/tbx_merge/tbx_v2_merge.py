import argparse
from pathlib import Path
from xml.etree import ElementTree as et

class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class XMLCombiner(object):
    def __init__(self, filenames):
        if len(filenames) == 0:
            raise FileNotFoundError('Invalid path, or path contains no valid files.')
        
        self.roots = [et.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            self.combine_element(self.roots[0], r)
        return et.ElementTree(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively combines text, attributes, and children of an xml element tree.
        It updates either the text/attributes/children of an element if another element is found in `one`,
        or adds it from `other` if not found.
        """
        mapping = {(el.tag, hashabledict(el.attrib)): el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    mapping[(el.tag, hashabledict(el.attrib))].text = el.text
                except KeyError:
                    # Element not found in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    one.append(el)
            else:
                # Nested
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[(el.tag, hashabledict(el.attrib))], el)
                except KeyError:
                    # Element not found in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    one.append(el)

def extract_smartling_id_term(f):
    """"Creates a dictionary with (term, definition) as key, and the Smartling UID as value."""
    root = et.parse(f).getroot()
    smartling_dict = {}
    for termEntry in root.iter('termEntry'):
        term = termEntry.find("./langSet[@{http://www.w3.org/XML/1998/namespace}lang='en-US']/tig/term").text
        try:
            definition = termEntry.find("./descrip[@type='definition']").text
        except AttributeError:
            definition = None
        id = termEntry.attrib['id']
        smartling_dict[(term, definition)] = id

    return smartling_dict

def replace_pontoon_ids(etree, smartling_dict):
    """Replaces Pontoon IDs with Smartling IDs if the term and definition match exactly a term in Smartling glossary file."""
    root = etree.getroot()
    pontoon_term_map = {}
    for termEntry in root.iter('termEntry'):
        term = termEntry.find("./langSet[@{http://www.w3.org/XML/1998/namespace}lang='en-US']/ntig/termGrp/term").text
        try:
            definition = termEntry.find("./langSet[@{http://www.w3.org/XML/1998/namespace}lang='en-US']/descripGrp/descrip[@type='definition']").text
        except AttributeError:
            definition = None
        pontoon_term_map[(term, definition)] = termEntry
    
    for key in pontoon_term_map:
        if key in smartling_dict:
            pontoon_term_map[key].attrib['id'] = smartling_dict[key]
        else:
            pontoon_term_map[key].attrib.pop('id', None)

def remove_all_ids(etree):
    """Smartling system only accepts IDs it creates. This removes all IDs so all terms will be registered as new."""
    root = etree.getroot()
    
    for termEntry in root.iter('termEntry'):
        termEntry.attrib.pop('id', None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pontoon", required=True, dest="pontoon_exports", help="Pontoon tbx export directory")
    parser.add_argument("--export")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--smartling", dest="smartling_export", help="Merges Pontoon terminology for multiple locales and modifies/removes IDs to allow for importing into Smartling. Requires specifying path to Smartling glossary export tbx file.")
    group.add_argument("--merge_only", action="store_true", help="Merges Pontoon terminology for multiple locales without altering IDs.")
    group.add_argument("--new", action="store_true", help="Merges Pontoon terminolgy for multiple locales and removes all IDs. Use this when creating a new glossary in Smartling.")
    args = parser.parse_args()


    merge_files = list(Path(args.pontoon_exports).glob('*.tbx'))
    merged_tree = XMLCombiner(merge_files).combine()

    if args.merge_only:
        merged_tree.write("pontoon_glossary_multilingual.tbx", encoding="UTF-8", xml_declaration=True)

    if args.smartling_export:
        smartling_dict = extract_smartling_id_term(args.smartling_export)
        replace_pontoon_ids(merged_tree, smartling_dict)
        merged_tree.write('smartling_glossary_existing.tbx', encoding="UTF-8", xml_declaration=True)

    if args.new:
        remove_all_ids(merged_tree)
        merged_tree.write('smartling_glossary_new.tbx', encoding="UTF-8", xml_declaration=True)

if __name__ == '__main__':
    main()
