#!/usr/bin/python3

import re
import os
import sys
import shutil

import requests
import bs4


OFFICIAL_ARCHIVE = 'official_archive'
OFFICIAL_URL = 'http://files.sunnysubs.com/files/'
MLP_iTunes_regex = re.compile(r'^Sub_MLPFiM_S\d{2}E.+?_iTunes.*?.ass$')


def log(message):
    print(message, file=sys.stderr)


def good_link(link_text):
    for banned in ('S01', 'temp'):
        if banned in link_text:
            return False
    if MLP_iTunes_regex.match(link_text):
        return True
    return False


def archive_dir(filename):
    return os.path.join(OFFICIAL_ARCHIVE, filename)


log('Obtaining official subs from ' + OFFICIAL_URL)
try:
    response = requests.get(OFFICIAL_URL)
except:
    log('Failed to get official subs for unknown reason.')
    exit(66)

log('Parsing response')
try:
    dom_tree = bs4.BeautifulSoup(response.content, 'html5lib')
except:
    log('Parsing error!')
    exit(67)

log('Downloading links')
if not os.path.isdir(OFFICIAL_ARCHIVE):
    os.mkdir(OFFICIAL_ARCHIVE)
failed_hrefs = []
for link in dom_tree.find_all('a'):
    try:
        href = link['href']
    except KeyError:
        continue
    if good_link(href):
        log('Fetching ' + href)
        try:
            response = requests.get(OFFICIAL_URL + href)
        except:
            log('Failed to get %s for unknown reason.' % href)
            failed_hrefs.append(href)
        with open(archive_dir(href), 'wb') as sub_file:
            sub_file.write(response.content)
        log(href + ' is successfully saved')

log('\nAll links processed!\n')
if len(failed_hrefs) == 0:
    log('No fetch failed!\n')
else:
    log('Failed to fetch the following files:')
    log('\n'.join(failed_hrefs) + '\n')

log('Copying files to corresponding directories')
for filename in os.listdir(OFFICIAL_ARCHIVE):
    if good_link(filename):
        season = int(re.search(r'S(\d{2})', filename).group(1))
        shutil.copy(archive_dir(filename),
                    os.path.join('Season' + str(season), filename))

log('Update completed!')
