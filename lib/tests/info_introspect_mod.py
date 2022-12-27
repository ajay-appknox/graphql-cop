from lib.utils import graph_query, curlify

def introspection_mod(url, proxy, headers):
  """Run introspection."""
  res = {
    'result':False,
    'title':'Introspection Mod',
    'description':'Introspection Query Enabled',
    'impact':'Information Leakage - /' + url.rsplit('/', 1)[-1],
    'severity':'HIGH',
    'curl_verify':'',
    'response':''
  }

  q = 'query cop {__schema{queryType{name}mutationType{name}subscriptionType{name}types{...FullType}directives{name description locations args{...InputValue}}}}fragment FullType on __Type{kind name description fields(includeDeprecated:true){name description args{...InputValue}type{...TypeRef}isDeprecated deprecationReason}inputFields{...InputValue}interfaces{...TypeRef}enumValues(includeDeprecated:true){name description isDeprecated deprecationReason}possibleTypes{...TypeRef}}fragment InputValue on __InputValue{name description type{...TypeRef}defaultValue}fragment TypeRef on __Type{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name ofType{kind name}}}}}}}}'

  gql_response = graph_query(url, proxies=proxy, headers=headers, payload=q)
  res['curl_verify'] = curlify(gql_response)
  res['response'] = gql_response
  try:
    if gql_response.json()['data']['__schema']['types']:
      res['result'] = True
  except:
    pass

  return res
