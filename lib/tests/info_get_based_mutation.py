"""Checks mutation support over on GET."""
from lib.utils import request, curlify


def get_based_mutation(url, proxies, headers):
  res = {
    'result':False,
    'title':'Mutation is allowed over GET (possible CSRF)',
    'description':'GraphQL mutations allowed using the GET method',
    'impact':'Possible Cross Site Request Forgery - /' + url.rsplit('/', 1)[-1],
    'severity':'MEDIUM',
    'curl_verify':'',
    'response':''
  }

  q = 'mutation cop {__typename}'

  response = request(url, proxies=proxies, headers=headers, params={'query':q})
  res['curl_verify'] = curlify(response)
  try:
    if response and response.json()['data']['__typename']:
        res['result'] = True
  except:
      pass

  return res
