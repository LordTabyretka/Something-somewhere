import requests

from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def clean_text(text):
    return " ".join(text.split())


def get_node_name(dot):
    parts = []

    for element in dot.next_siblings:
        if getattr(element, "name", None) == "a":
            break

        if isinstance(element, NavigableString):
            text = str(element)
        else:
            text = element.get_text(" ", strip=True)

        text = clean_text(text)

        if text:
            parts.append(text)

    node_name = clean_text(" ".join(parts))

    if node_name:
        return node_name

    return "Сервер"


def change_port_in_url(proxy_url, new_port):
    parsed_url = urlparse(proxy_url)

    query_params = parse_qsl(parsed_url.query, keep_blank_values=True)

    new_query_params = []
    port_was_found = False

    for key, value in query_params:
        if key == "port":
            new_query_params.append((key, str(new_port)))
            port_was_found = True
        else:
            new_query_params.append((key, value))

    if not port_was_found:
        new_query_params.append(("port", str(new_port)))

    new_query = urlencode(new_query_params)

    return urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))


def get_user_url(url, port):
    if not url:
        return []

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.text, 'lxml')

    all_blocks = soup.select('div.node.online')

    result = []

    for block in all_blocks:
        dot = block.select_one('.dot.online')
        link = block.select_one('a.btn')

        if not dot or not link:
            continue

        node_name = get_node_name(dot)

        href = link.get('href')

        if not href:
            continue

        href_with_user_port = change_port_in_url(href, port)

        result.append({
            'country': node_name,
            'url': href_with_user_port
        })

    return result