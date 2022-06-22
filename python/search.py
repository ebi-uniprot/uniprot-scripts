#!/usr/bin/env python3
import re
import urllib
import requests
from requests.adapters import HTTPAdapter, Retry

re_next_link = re.compile(r'<(.+)>; rel="next"')

retries = Retry(total=5, backoff_factor=0.25, status_forcelist=[500, 502, 503, 504])
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retries))


def fetch(url):
    response = session.get(url)
    if not response.ok:
        raise Exception(response.reason)
    return response


def get_next_link(headers):
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)


def get_total(headers):
    if "x-total-records" in headers:
        return int(headers["x-total-records"])


def search_pagination(query, size=100, namespace="uniprotkb"):
    params = {"query": query, "size": size}
    endpoint = f"https://rest.uniprot.org/{namespace}/search"
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    n_results = 0
    while url:
        response = fetch(url)
        total = get_total(response.headers)
        results = response.json()["results"]
        n_results += len(results)
        print(f"fetched {n_results}/{total}")
        yield results
        url = get_next_link(response.headers)


def search_stream(query, namespace="uniprotkb"):
    params = {
        "query": query,
    }
    endpoint = f"https://rest.uniprot.org/{namespace}/stream"
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    response = fetch(url)
    return response.json()["results"]


def main():
    query = "cdc7 human"
    results_pagination = [r for batch in search_pagination(query, 50) for r in batch]
    results_stream = search_stream(query)
    assert len(results_pagination) == len(results_stream)


if __name__ == "__main__":
    main()
