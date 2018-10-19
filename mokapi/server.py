import json
import logging

import bottle

from spec_server import SpecServer, HttpVerb

LOGGER = logging.getLogger('mokapi.server')

app = bottle.Bottle()
spec_server = None


@app.route('/<uri:re:.*>', method=[v.value.upper() for v in HttpVerb])
def mock_api_router(uri):
  if not spec_server:
    LOGGER.error('Spec Server not Initialized')

  try:
    http_verb = HttpVerb[bottle.request.method]
  except KeyError:
    bottle.abort(500, 'Invalid HTTP method')

  matched_route = spec_server.get_route('/' + uri, http_verb)
  if not matched_route:
    LOGGER.warning('Unable to find a matching route for uri | %s | %s', http_verb, uri)
    bottle.abort(404, 'Not Found')

  LOGGER.debug('Discovered matching Route: %s', matched_route)
  page = None
  count = 10
  resp = matched_route.response
  for key, value in bottle.request.query.items():
    if key not in matched_route.query_params:
      LOGGER.warning('Provided query param is not in the spec | %s', key)
      continue

    if key == 'page':
      page = abs(int(value))
      continue

    if key == 'count':
      count = abs(int(value))
      continue

    resp = [r for r in resp if str(r.get(key)).lower() == value.lower()]

  if page is not None:  # 0 is a valid value
    start_index = min([count * (page - 1), len(resp)])
    end_index = min([start_index + count, len(resp)])

    LOGGER.debug('Paging request | Page: %s | Count %s | Start Index: %s | End Index: %s',
                 page,
                 count,
                 start_index,
                 end_index)
    resp = resp[start_index:end_index]

  LOGGER.debug('Returning resp: %s', resp)
  return json.dumps(resp)


def serve(spec, host='0.0.0.0', port='8000'):
  global spec_server

  spec_server = SpecServer(spec)

  LOGGER.info('Starting up... listening on %s:%s', host, port)
  bottle.run(app, host=host, port=port, reloader=True)
