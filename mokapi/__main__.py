#!/usr/bin/env python
"""
Open API Mocker

Usage:
  mokapi <spec-file> [options]

Options:
  -p --port PORT  Change serving port. [default: 8000]
  -v --verbose    Toggle extra verbosity.
  -h --help       Display this help dialog.

"""
import logging
import sys

import yaml
from docopt import docopt

import server
from __version__ import version

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger('mokapi')


def parse_args():
  return docopt(__doc__, version=version)


def main():
  args = parse_args()
  if args['--verbose']:
    LOGGER.setLevel(logging.DEBUG)

  try:
    with open(args['<spec-file>'], 'r') as f:
      spec = yaml.safe_load(f)
  except FileNotFoundError:
    LOGGER.error('Cannot open provided spec file: %s', args['<spec-file>'])
    return 1

  server.serve(spec, port=args['--port'])


if __name__ == '__main__':
  sys.exit(main())
