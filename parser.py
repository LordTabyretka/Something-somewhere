from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


def flag_to_country_code(flag):
    flag = flag.strip()

    return ''.join(
        chr(ord(ch) - ord('🇦') + ord('A'))
        for ch in flag
    )


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
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )

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

        flag = dot.parent.get_text(strip=True)
        country = flag_to_country_code(flag)

        href = link.get('href')

        if not href:
            continue

        href_with_user_port = change_port_in_url(href, port)

        result.append({
            'country': country,
            'url': href_with_user_port
        })

    return result
