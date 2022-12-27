"""Perform introspection tests."""
from lib.utils import graph_query, curlify


def introspection(url, proxy, headers):
  """Run introspection."""
  res = {
    'result':False,
    'title':'Introspection',
    'description':'Introspection Query Enabled',
    'impact':'Information Leakage - /' + url.rsplit('/', 1)[-1],
    'severity':'HIGH',
    'curl_verify':'',
    'response':''
  }

  q = 'query cop { __schema { types { name fields { name } } } }'

  gql_response = graph_query(url, proxies=proxy, headers=headers, payload=q)
  res['curl_verify'] = curlify(gql_response)
  res['response'] = gql_response
  try:
    if gql_response.json()['data']['__schema']['types']:
      res['result'] = True
  except:
    pass

  return res
