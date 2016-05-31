#!/usr/bin/python

import subprocess
import os
import urllib2
import json
import math

limit = '100'
default = 'NaN'

def get_url(name, limit=limit):
    return 'https://api.github.com/search/repositories?q=user:' + name + '+fork:true&per_page=' + limit

def get_data(url, pageNumber=default):
    'grab repository data for username'
    if pageNumber != default:
        url = url + '&page=' + str(pageNumber)
    response = urllib2.urlopen(url)
    data = json.load(response)
    return data

def clone_repo(repoName, repoUrl, dest):
    'clone a GitHub repository to the desired location'
    output = subprocess.check_output(['git', 'clone', repoUrl, dest + repoName])
    return output

def update_repo(repoName, dest):
    'pulls changes for a clone GitHub repo'
    output = subprocess.check_output(['git', '-C', dest + repoName, 'pull'])
    return output

def process_repos(repos, loc):
    for repo in repos:
        print 'backing up', repo['name']
        if os.path.isdir(loc + repo['name']):
            print 'updating', repo['name']
            print update_repo(repo['name'], loc)
        else:
            print clone_repo(repo['name'], repo['clone_url'], loc)



###


repos = []


# Get username and destination
username = raw_input('Enter the username/organisation you wish to back up repos for: ')
# Inform of the current location
print 'You are currently located @ ' + subprocess.check_output(['pwd'])
loc      = raw_input('Enter the location for your backups (defaults to "./backups/"): ')

# Generate the Github API url with the given username
url = get_url(username)

# Process backup destination
if loc.strip() == '':
    loc = './backups/'

# Get first round of data from API request.
data = get_data(url)

# If there are no items, there is nothing to back up else set repos to items returned.
if len(data['items']) > 0:
    repos = data['items']
else:
    print 'No repos to backup'

# Check if there are more repos to request, if there are, recursively get paged data until all repo urls are obtained.
if data['total_count'] > int(limit, 10):
    pages = math.ceil(data['total_count'] / float(limit))
    # Start at page 2 because we already have page 1
    page = 2
    while page <= pages:
        newData = get_data(url, page)
        if len(newData['items']) > 0:
            repos += newData['items']
        page = page + 1

# Process the repo data, either updating or cloning
process_repos(repos, loc)
