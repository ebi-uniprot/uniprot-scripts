#!/usr/bin/env python3
import re
import urllib
import requests

re_next_link = re.compile(r'<(.+)>; rel="next"')


def fetch(url):
    response = requests.get(url)
    if not response.ok:
        raise Exception(response.reason)
    return response


def get_next_link(response):
    headers = response.headers
    if "Link" in headers:
        match = re_next_link.match(headers["Link"])
        if match:
            return match.group(1)


def get_total(response):
    headers = response.headers
    if "x-total-records" in headers:
        return int(headers["x-total-records"])


def search_pagination(query, size=500, namespace="uniprotkb"):
    params = {"query": query, "size": size}
    endpoint = f"https://rest.uniprot.org/{namespace}/search"
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    n_results = 0
    while url:
        results_response = fetch(url)
        total = get_total(results_response)
        results = results_response.json()["results"]
        n_results += len(results)
        print(f"fetched {n_results}/{total}")
        yield results
        url = get_next_link(results_response)


def search_stream(query, namespace="uniprotkb"):
    params = {
        "query": query,
    }
    endpoint = f"https://rest.uniprot.org/{namespace}/stream"
    url = f"{endpoint}?{urllib.parse.urlencode(params)}"
    results_response = fetch(url)
    return results_response.json()["results"]


query = "cdc7 human"
results_pagination = [r for batch in search_pagination(query, 50) for r in batch]
results_stream = search_stream(query)
assert results_pagination == results_stream
