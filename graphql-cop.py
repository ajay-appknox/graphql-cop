#!/usr/env/python3
import sys, os, re

from json import loads
from json import dumps
from optparse import OptionParser
from version import VERSION
from config import HEADERS, SAVE_RESULTS
from urllib.parse import urlparse
from requests_toolbelt.utils import dump

from lib.tests.info_field_suggestions import field_suggestions
from lib.tests.info_introspect import introspection
from lib.tests.info_introspect_mod import introspection_mod
from lib.tests.info_graphiql import detect_graphiql
from lib.tests.info_get_method_support import get_method_support
from lib.tests.dos_alias_overloading import alias_overloading
from lib.tests.dos_batch import batch_query
from lib.tests.dos_field_duplication import field_duplication
from lib.tests.dos_directive_overloading import directive_overloading
from lib.tests.info_trace_mode import trace_mode
from lib.tests.dos_circular_introspection import circular_query_introspection
from lib.tests.info_get_based_mutation import get_based_mutation
from lib.tests.info_post_based_csrf import post_based_csrf
from lib.tests.info_unhandled_error import unhandled_error_detection
from lib.utils import is_graphql, draw_art

parser = OptionParser(usage='%prog -t http://example.com -o json')
parser.add_option('-t', '--target', dest='url', help='target url with the path - if a GraphQL path is not provided, GraphQL Cop will iterate through a series of common GraphQL paths')
parser.add_option('-H', '--header', dest='header', action='append', help='Append Header(s) to the request \'{"Authorization": "Bearer eyjt"}\' - Use multiple -H for additional Headers')
parser.add_option('-o', '--output', dest='format',
                        help='json', default=False)
parser.add_option('-f', '--force', dest='forced_scan', action='store_true',
                        help='Forces a scan when GraphQL cannot be detected', default=False)          
parser.add_option('-s', '--save', dest='save_results', action='store_true',
                        help='Save output of the scan in report format', default=False)                        
parser.add_option('--proxy', '-x', dest='proxy', action='store_true', default=False,
                        help='Sends the request through http://127.0.0.1:8080 proxy')
parser.add_option('--version', '-v', dest='version', action='store_true', default=False,
                        help='Print out the current version and exit.')


options, args = parser.parse_args()

if options.version:
    print('version:', VERSION)
    sys.exit(0)
    
if options.save_results:
    SAVE_RESULTS = True

if not options.url:
    print(draw_art())
    parser.print_help()
    sys.exit(1)

if options.proxy == True:
    proxy = {
        'http':  'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
else:
    proxy = {}

if options.header != None:
    try:
        for l in options.header:
            extra_headers = loads(l)
            HEADERS.update(extra_headers)
    except:
        print("Cannot cast %s into header dictionary. Ensure the format \'{\"key\": \"value\"}\'."%(options.header))

if not urlparse(options.url).scheme:
    print("URL missing scheme (http:// or https://). Ensure URL contains some scheme.")
    sys.exit(1)
else:
    url = options.url

endpoints = ['/graphiql', '/playground', '/console', '/graphql']
paths = []
parsed = urlparse(url)

if parsed.path and parsed.path != '/':
    paths.append(url)
else:
     for endpoint in endpoints:
        paths.append(parsed.scheme + '://' + parsed.netloc + endpoint)

tests = [field_suggestions]#field_suggestions, introspection] #, detect_graphiql,
        #  get_method_support, alias_overloading, batch_query,
        #  field_duplication, trace_mode, directive_overloading,
        #  circular_query_introspection, get_based_mutation, post_based_csrf,
        #  unhandled_error_detection]

json_output = []

for path in paths:
    if not is_graphql(path, proxy, HEADERS):
        if not options.forced_scan:
            print(path, 'does not seem to be running GraphQL. (Consider using -f to force the scan if GraphQL does exist on the endpoint)')
            continue
        else:
            print('Running a forced scan against the endpoint')
    for test in tests:
        json_output.append(test(path, proxy, HEADERS))

json_output = sorted(json_output, key=lambda d: d['title']) 

if options.format == 'json':
    print(dumps(json_output))
else:
    for i in json_output:
        if i['result']:
            print('[{}] {} - {} ({}) - {}'.format(i['severity'], i['title'], i['description'], i['impact'], len(i['response'].text)))
            if options.save_results:
                if not os.path.exists("/tmp/graphql_cop"):
                    os.mkdir("/tmp/graphql_cop")
                with open("/tmp/graphql_cop/%s" % i['title'].lower().replace(" ", "_"), "w") as fd:
                    tmp_res = dump.dump_response(i['response'], request_prefix=b'', response_prefix=b'').decode().replace("CONNECT", "POST")
                    # tmp_res = re.sub(r'^< |^> ', '', tmp_res, flags=re.MULTILINE)
                    print(tmp_res)
                    fd.write(tmp_res)
