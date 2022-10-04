#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -r repo_path -p pull_SHA -c config_path"
   echo -e "\t-r Path to repository"
   echo -e "\t-p Pull request SHA)"
   echo -e "\t-c moz-fluent-lint config path"
   exit 1 # Exit script after printing help
}

while getopts "r:p:c:" opt
do
   case "$opt" in
      r ) repo_path="$OPTARG" ;;
      p ) pull_SHA="$OPTARG" ;;
      c ) config_path="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$repo_path" ] || [ -z "$pull_SHA" ] || [ -z "$config_path" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
cd $repo_path
git fetch upstream
git merge upstream/main

diff=$( git diff --name-only HEAD $pull_SHA )
for file in $diff; do
    mkdir -p "temp_head/${file%/*}/"
    git show $pull_SHA:$file > temp_head/$file
done

moz-fluent-lint temp_head $config_path

rm -rf temp_head
