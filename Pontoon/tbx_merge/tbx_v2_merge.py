import re
import sys
from xml.etree import ElementTree as et


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class XMLCombiner(object):
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        # save all the roots, in order, to be processed later
        self.roots = [et.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            # combine each element with the first one, and update that
            self.combine_element(self.roots[0], r)
        # return the string representation
        return et.ElementTree(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively updates either the text or the children
        of an element if another element is found in `one`, or adds it
        from `other` if not found.
        """
        # Create a mapping from tag name to element, as that's what we are fltering with
        mapping = {(el.tag, hashabledict(el.attrib)): el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    mapping[(el.tag, hashabledict(el.attrib))].text = el.text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # Add it
                    one.append(el)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[(el.tag, hashabledict(el.attrib))], el)
                except KeyError:
                    # Not in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # Just add it
                    one.append(el)

def remove_all_ids(f):
    """Smartling cannot use IDs assigned by Pontoon, so they must be removed to import as a new glossary"""
    result = ""
    with open(f) as file:
        result = re.sub(r"(termEntry)( id=.*)(>)", r"\g<1>\g<3>", file.read())
    
    with open(f, "w") as file:
        file.write(result)

def remove_new_ids(f):
    pass

def extract_smartling_id_term(f):
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

def convert_ids(f, smartling_dict):
    root = et.parse(f).getroot()
    pontoon_term_map = {}
    for termEntry in root.iter('termEntry'):
        term = termEntry.find("./langSet[@{http://www.w3.org/XML/1998/namespace}lang='en-US']/ntig/termGrp/term").text
        try:
            definition = termEntry.find("./langSet[@{http://www.w3.org/XML/1998/namespace}lang='en-US']/descripGrp/descrip[@type='definition']").text
        except AttributeError:
            definition = None
        pontoon_term_map[(term, definition)] = termEntry
    
    for key, value in smartling_dict.items():
        if key in pontoon_term_map:
            pontoon_term_map[key].attrib['id'] = value
    
    return et.ElementTree(root)

if __name__ == '__main__':

    r = XMLCombiner(sys.argv[1:]).combine()
    r.write('import_test.tbx', encoding="UTF-8", xml_declaration=True)
    smartling_dict = extract_smartling_id_term('import_test_export.tbx')
    w = convert_ids('import_test.tbx', smartling_dict)
    w.write('test_test_modifications.tbx', encoding="UTF-8", xml_declaration=True)
    remove_all_ids('import_test.tbx')
