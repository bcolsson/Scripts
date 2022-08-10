# TBX Merge tool documentation

## Summary

The tbx_merge tool exports, merges, and prepares terminology for import into Smartling via a tbx (v2) file.

## Requirements

To run the script you will need the following:
- Python (tested working on version 3.10)
- requests module
- List of locales you wish to extract from Pontoon (see "locales.txt" for example)

***If importing terms into an existing glossary on Smartling***
- A tbx format glossary export from Smartling

## Syntax

Call tbx_merge.py from your command line, with the following arguments:

--locales *filepath*  
(***Required***) Designate the filepath of a .txt file that contains the list of Pontoon locale codes (separated by newline) you would like to extract from Pontoon and merge.

--id-format (*smartling, new, pontoon*)  
Select from one of three strategies for dealing with termEntry IDs.

*smartling*: This will apply the UID Smartling uses to manage glossary terms to any Pontoon terms that match. Any terms not in Smartling will have their Pontoon ID removed for import into Smartling as a new term. This requires a tbx file exported from Smartling to match and assign IDs. The file will need to be identified by the separate argument --smartling.
**Note:** This script uses the term and definition to match between Pontoon and Smartling. Any manual changes made to either a term or definition in either Pontoon or Smartling will cause the script to flag it as a new term.  
Outputs: smartling_merge_glossary.tbx

*new*: This will remove all Pontoon IDs for all termEntry elements, causing all terminology to be treated as a new term upon import into Smartling. Typically this would be used if creating a new glossary from scratch.  
Outputs: smartling_new_glossary.tbx

*pontoon*: This will preserve all Pontoon IDs. Smartling will not be able to import the resulting file as Smartling requires the UIDs to be assigned by its platform.  
Outputs: pontoon_glossary_multilingual.tbx

--smartling *filepath*  
(***Required if --id-format smartling argument selected***) Designate the filepath of a .tbx file exported from Smartling.

## Importing into Smartling

## Exporting Smartling glossary for merge
