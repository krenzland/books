#!/bin/bash
# See https://github.com/steveklabnik/automatically_update_github_pages_with_travis_example
set -o errexit -o nounset

if [ "$TRAVIS_BRANCH" != "master" ];
then
    echo "Commit against $TRAVIS_BRANCH, and not master. Don't deploy."
    exit 0
fi

# We're building against revision...
rev=$(git rev-parse --short HEAD)

# Decrypt deploy key
openssl aes-256-cbc -K $encrypted_6a6599eb477f_key -iv $encrypted_6a6599eb477f_iv -in id_rsa.enc -out id_rsa -d
chmod 600 id_rsa
eval `ssh-agent -s`
ssh-add id_rsa

rm -rf posts/.gitkeep
rm -rf lists/.gitkeep

# Set up git at site folder.
git init
git config user.name "Lukas Krenz"
git config user.email "lukas@krenz.land"

# Reset current repo to upstream.
git remote add upstream "git@github.com:krenzland/books.git"
git fetch upstream
git reset upstream/reviews

# Add all files
touch .
git add -A posts/
git add -A lists/

# Push
git commit -m "Auto-build, rev=${rev}"
git push -q upstream HEAD:reviews
