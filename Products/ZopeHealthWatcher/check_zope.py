#!/usr/bin/python
""" Zope Health Controller - inspired from :

- DeadlockDebugger : http://plone.org/products/deadlockdebugger

- MonitoringExchange :
  http://www.monitoringexchange.org/cgi-bin/page.cgi?g=Detailed%2F1354.html;d=1

"""
import sys
from ConfigParser import SafeConfigParser
from urllib import FancyURLopener

OK = (0, 'OK - %s')
WARNING = (1, 'WARNING - %s')
FAILURE = (2, 'FAILURE - %s')
CRITICAL = (3, 'CRITICAL - %s')


class ZHCOpener(FancyURLopener):
    version = 'ZopeHealthController'


class ZopeHealthWatcher(object):

    def __init__(self):
        parser = SafeConfigParser()
        parser.read('zopehealthwatcher.ini')
        self.SECRET = parser.get('ZopeHealthWatcher', 'SECRET')
        self.DUMP_URL = '/manage_zhw'
        self.SDUMP_URL = self.DUMP_URL + '?' + self.SECRET

    def _read_url(self, url):
        return ZHCOpener().open(url).read()

    def _(self, status, msg):
        return status[0], status[1] % msg

    def query_zope(self, url):
        """Queries a Zope server"""
        data = self._read_url(url)

        lines = data.split('\n')
        # reading the modules
        modules = []
        for index, line in enumerate(lines):
            line = line.strip()
            if line == '':
                continue
            if line == '***':
                break
            line = line.split()
            name = line[0]
            data = ' '.join(line[1:])
            modules.append((name, data))

        # now reading the rest of the dump
        idle = 0
        busy = 0
        index += 1
        dump = index
        while index < len(lines):
            if lines[index].startswith('Thread'):
                if index + 1 < len(lines) and lines[index+1] == 'not busy':
                    idle += 1
                    index += 2
                else:
                    busy += 1
                    # jump to the next Thread
                    index += 1
                    while (index < len(lines) and
                           not lines[index].startswith('Thread')):
                        index += 1
            else:
                index += 1

        return modules, lines[dump:], idle, busy

    def get_result(self, url):
        try:
            modules, dump, idle, busy = self.query_zope(url)
        except Exception, e:
            return [], '', 0, 0, self._(FAILURE, str(e))
        if idle == 0:
            state = self._(CRITICAL,
                           'No more Threads on this client instance available')
        elif busy >= 4:
            state = self._(WARNING, 'Warning, high load')
        else:
            state = self._(OK, 'Everything looks fine')

        return modules, dump, idle, busy, state

    def main(self):
        url = sys.argv[1] + self.DUMP_URL
        print('call url: "%s"' % url)
        if self.secret:
            url += '?%s' % self.secret
        modules, dump, idle, busy, state = self.get_result(url)
        # only if state != 0
        if state[0] != 0:
            if len(modules) > 0:
                print('Information:')
            for name, value in modules:
                print('\t%s: %s' % (name, value))
            if len(dump) > 0:
                print('')
                print('Dump:')
                print('\n'.join(dump))
                print('')
        print('Threads: %s' % str(int(idle) + int(busy)))
        print('Idle: %s\nBusy: %s' % (idle, busy))
        print(state[1])
        sys.exit(state[0])


if __name__ == "__main__":
    ZopeHealthWatcher.main()
