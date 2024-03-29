import re
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl


def gen_next_page_url(url: str, param: str = "page") -> str:
  """
  Generate a URL to the next page using GET-param called 'page',
  incrementing its current value or setting a default one unless
  the param is defined in the URL.

  Examples:
    Input URL: https://auto.ria.com/uk/search
    Output URL: https://auto.ria.com/uk/search?page=1
    ======================================================================
    Input URL: https://auto.ria.com/uk/search/?categories.main.id=1&page=4
    Output URL: https://auto.ria.com/uk/search/?categories.main.id=1&page=5

  :param url: URL to update/set the page-param in
  :param param: name of the page-param
  :return: URL with the updated/set the page-param
  """
  url_parts = list(urlparse(url))
  page_param = re.search(fr"{param}=\d+", url_parts[4])
  page_group = {param: 0 if not page_param else int(page_param.group().split("=")[1])}
  page_group[param] += 1
  query = dict(parse_qsl(url_parts[4]), **page_group)
  url_parts[4] = urlencode(query)
  next_page_url = urlunparse(url_parts)
  return next_page_url
