import copy
import dataclasses
import logging
import random
import re
import time
import typing
import urllib.parse
import uuid
from datetime import datetime
from enum import Enum

LOGGER = logging.getLogger('mokapi.spec_server')


class HttpVerb(Enum):
  GET = 'get'
  POST = 'post'
  PUT = 'put'
  PATCH = 'patch'
  DELETE = 'delete'


@dataclasses.dataclass
class Route:
  path: str
  response: typing.Any
  method: HttpVerb = HttpVerb.GET
  query_params: typing.List[str] = dataclasses.field(default_factory=list)


class SpecServer(object):
  def __init__(self, spec):
    random.seed(int(time.time()))

    self._spec = spec
    self._route_prefix = self._get_route_prefix()
    self.routes = self._parse_routes(spec)

  def get_route(self, uri, method):
    for route in self.routes:
      if not route.method == method:
        continue

      LOGGER.debug('Testing route "%s" against uri "%s"', route, uri)
      if re.match(route.path, uri):
        LOGGER.info('Found matching route: %s', route.path)
        return route

  def _parse_routes(self, spec):
    paths = spec.get('paths')
    if not paths:
      return []

    routes = []
    path_param_matcher = re.compile(r'^[{<:][a-zA-Z0-9\-_]+?[}>]?$')
    for path, methods in paths.items():
      for method, definition in methods.items():
        query_params = []
        for parameter in definition.get('parameters', []):
          if parameter['in'] == 'query':
            query_params.append(parameter['name'].lower())

        path_with_substitutions = []
        for part in path.lower().split('/'):
          if path_param_matcher.match(part):
            path_with_substitutions.append('[a-zA-Z0-9\-_]+?')
          else:
            path_with_substitutions.append(part)

        response = None
        resp_definition = definition.get('responses', {}).get('200')
        if resp_definition:
          resp_content = resp_definition.get('content', {})

          # For now, I only care about json responses.
          json_content = resp_content.get('application/json')
          response = self._parse_response(json_content)

        routes.append(Route(path='^{0}{1}$'.format(self._route_prefix, '/'.join(path_with_substitutions)),
                            response=response,
                            method=HttpVerb[method.upper()],
                            query_params=query_params))

    return sorted(routes, key=lambda x: len(x.path), reverse=True)

  def _parse_response(self, resp):
    return self._parse_schema(resp.get('schema', {}))

  def _parse_schema(self, schema):
    if '$ref' in schema:
      ref_path = schema['$ref'].lstrip('#/').split('/')
      ref = copy.deepcopy(self._spec)
      for path in ref_path:
        ref = ref[path]
      schema = ref

    schema_type = schema.get('type')
    if schema_type == 'string':
      if 'enum' in schema:
        return random.choice(schema['enum'])

    if schema_type == 'object':
      obj = {}
      properties = schema.get('properties', {})
      for prop_name, definition in properties.items():
        if '$ref' in definition:
          obj[prop_name] = self._parse_schema(definition)
          continue

        default_value = definition.get('default')
        if default_value:
          obj[prop_name] = default_value
          continue

        prop_type = definition.get('type')
        if prop_type == 'string':
          prop_format = definition.get('format')
          if prop_format == 'uuid':
            obj[prop_name] = str(uuid.uuid4())
          elif prop_format == 'date-time':
            obj[prop_name] = datetime.now().isoformat()
          else:
            obj[prop_name] = 'Some Test String'

        elif prop_type in ['integer', 'number', 'long']:
          obj[prop_name] = random.randint(0, 10000)

        elif prop_type == 'array':
          obj[prop_name] = []
          for i in range(0, random.randint(1, 10)):
            obj[prop_name].append(self._parse_schema(definition.get('items')))

      return obj

    if schema_type == 'array':
      arr_obj = []
      for i in range(0, random.randint(5, 10)):
        arr_obj.append(self._parse_schema(schema.get('items', {})))

      return arr_obj

  def _get_route_prefix(self):
    servers = self._spec.get('servers', [])
    for server in servers:
      url = server.get('url')
      if not url:
        continue

      parsed_url = urllib.parse.urlparse(url)
      if parsed_url.path:
        return parsed_url.path
