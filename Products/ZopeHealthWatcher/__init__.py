# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id: __init__.py,v 1.1 2005/02/23 15:35:21 fguillaume Exp $

"""Debug running threads

This adds a ZServer hook so that if a special URL is called, a full dump
with tracebacks of the running python threads will be made.
"""
from Products.ZopeHealthWatcher.check_zope import ZopeHealthWatcher as zhw

try:
    from zLOG import LOG, INFO, ERROR
except ImportError:
    INFO = 0
    ERROR = 1
    import logging
    logger = logging.getLogger()

    def LOG(title, level, msg):
        if level == INFO:
            logger.info('%s %s' % (title, msg))
        else:
            logger.error('%s %s' % (title, msg))

if not zhw().SECRET:
    LOG('Products.ZopeHealthWatcher', ERROR,
        """Not activated, you must set a SECRET in a
file zopehealthwatcher.ini in your working directory.

The File should look like this:

[ZopeHealthWatcher]
SECRET = SECRET
""")

else:
    import dumper
    LOG('Products.ZopeHealthWatcher', INFO, "Installed & Activated")
