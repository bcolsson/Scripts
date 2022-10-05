#!/bin/bash
#Import environment variables: 
#repo_path: path to repo you're checking, e.g. ~/fxa
#temp_dir: path to create temp dir that will be deleted

source ./env.txt

helpFunction()
{
   echo ""
   echo "Usage: $0 -p pull_SHA"
   echo -e "\t-p GitHub pull request ID)"
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
if [ -z "$pull_ID" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct

# Update fxa repo
cd $repo_path
git checkout main
git fetch upstream
git merge upstream/main

# Setup environment
yarn workspaces focus fxa-content-server
cd ./packages/fxa-content-server

# Delete local copies of .pot files, if they exist
rm -r locale/templates/LC_MESSAGES/*

# Extract gettext from base
npx grunt l10n-extract

# Copy to temp
mkdir -p $temp_dir
cp -a locale/templates/LC_MESSAGES/.  $temp_dir/
ls $temp_dir

# Fetch PR branch from github and create temp branch
git fetch upstream pull/$pull_ID/head:TEMP
git checkout TEMP

# Extract gettext from pull request
npx grunt l10n-extract

# Compare diff
echo "Diff of client.pot"
diff $temp_dir/client.pot locale/templates/LC_MESSAGES/client.pot
echo ""

echo "Diff of server.pot"
diff $temp_dir/server.pot locale/templates/LC_MESSAGES/server.pot
echo ""

echo "complete"

git checkout main
git branch -D TEMP
rm -rf $temp_dir
