#!/usr/bin/python -tt
# Copyright (C) 2013 by The Linux Foundation and contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys

import json

import logging

from fcntl import flock, LOCK_EX, LOCK_UN

VERSION = '0.2'
MANIFEST_LOCKH = None

# default logger. Will probably be overridden.
logger = logging.getLogger(__name__)

def find_all_gitdirs(toplevel):
    logger.info('Finding bare git repos in %s' % toplevel)
    gitdirs = []
    for root, dirs, files in os.walk(toplevel, topdown=True):
        if not len(dirs):
            continue

        torm = []
        for name in dirs:
            if name.find('.git') > 0:
                logger.debug('Found %s' % os.path.join(root, name))
                gitdirs.append(os.path.join(root, name))
                torm.append(name)

        for name in torm:
            # don't recurse into the found *.git dirs
            dirs.remove(name)

    return gitdirs

def manifest_lock(manifile):
    (dirname, basename) = os.path.split(manifile)
    MANIFEST_LOCKH = open(os.path.join(dirname, '.%s.lock' % basename), 'w')
    flock(MANIFEST_LOCKH, LOCK_EX)

def manifest_unlock(manifile):
    if MANIFEST_LOCKH is not None:
        flock(lockfh, LOCK_UN)
        lockfh.close()

def read_manifest(manifile):
    if not os.path.exists(manifile):
        return {}

    if manifile.find('.gz') > 0:
        import gzip
        fh = gzip.open(manifile, 'rb')
    else:
        fh = open(manifile, 'r')

    logger.info('Reading %s' % manifile)
    try:
        manifest = json.load(fh)
    except:
        # We'll regenerate the file entirely on failure to parse
        manifest = {}

    fh.close()

    return manifest

def write_manifest(manifile, manifest, mtime=None):
    import tempfile
    import shutil
    import gzip

    (dirname, basename) = os.path.split(manifile)
    (fd, tmpfile) = tempfile.mkstemp(prefix=basename, dir=dirname)
    logger.info('Writing new %s' % manifile)
    try:
        if manifile.find('.gz') > 0:
            fh = gzip.open(tmpfile, 'wb')
        else:
            fh = open(tmpfile, 'w')
        # Probably should make indent configurable, but extra whitespaces
        # don't change the size of manifest.js.gz by any appreciable amount
        json.dump(manifest, fh, indent=2)
        fh.close()
        os.chmod(tmpfile, 0644)
        if mtime is not None:
            os.utime(tmpfile, (mtime, mtime))
        shutil.move(tmpfile, manifile)

    finally:
        # If something failed, don't leave these trailing around
        if os.path.exists(tmpfile):
            os.unlink(tmpfile)

