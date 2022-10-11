#!/bin/bash
#Requires: moz-fluent-lint and compare_locales

#Import environment variables: 
#repo_path: path to repo you're checking, e.g. ~/fxa
#config_path: path to linter_config.yml
#detect_unchanged_ids: path to detect_unchanged_ids script
source ./env.txt

helpFunction()
{
   echo ""
   echo "Usage: $0 -p pull_SHA"
   echo -e "\t-p Pull request SHA)"
   exit 1 # Exit script after printing help
}

while getopts "p:" opt
do
   case "$opt" in
      p ) pull_SHA="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$pull_SHA" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
cd $repo_path
git checkout main
git fetch upstream
git merge upstream/main

diff=$( git diff --name-only HEAD $pull_SHA )
for file in $diff; do
    mkdir -p "temp_base/${file%/*}/" && mkdir -p "temp_head/${file%/*}/"
    git show HEAD:$file > temp_base/$file
    git show $pull_SHA:$file > temp_head/$file
done

echo "Linting for brand names"
moz-fluent-lint temp_head $config_path

echo "Checking for unchanged ids"
python $detect_unchanged_ids --base_dir temp_base --head_dir temp_head --locale_dir locale/en

rm -rf temp_head
rm -rf temp_base
