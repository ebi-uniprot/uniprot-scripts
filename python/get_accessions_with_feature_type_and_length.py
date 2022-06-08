#!/usr/bin/env python3
import re

from search import search_stream


def filter_feature_type_and_length(
    result, ft_type, re_ft_description, ft_min_length, ft_max_length
):
    features = result["features"]
    for feature in features:
        if ft_type == feature["type"].lower() and re_ft_description.search(
            feature["description"]
        ):
            start = feature["location"]["start"]["value"]
            end = feature["location"]["end"]["value"]
            length = end - start + 1
            if (ft_min_length == "*" or length >= ft_min_length) and (
                ft_max_length == "*" or length <= ft_max_length
            ):
                return True
    return False


def get_accessions_with_feature_type_and_length(
    ft_type, ft_description, ft_min_length, ft_max_length, and_query=None
):
    and_query = f" AND {and_query}" if and_query else ""
    query = f"(ft_{ft_type}:{ft_description} AND ftlen_{ft_type}:[{ft_min_length} TO {ft_max_length}]){and_query}"
    results = search_stream(query)
    re_ft_description = re.compile(
        ft_description.replace(" ", "[- /()]+"), re.IGNORECASE
    )
    return [
        result["primaryAccession"]
        for result in results
        if filter_feature_type_and_length(
            result,
            ft_type.lower(),
            re_ft_description,
            ft_min_length,
            ft_max_length,
        )
    ]


print(
    '''Equivalent to legacy.uniprot.org request:
  annotation:(type:motif 9aatad length:[10 TO *]) AND organism:"Homo sapiens (Human) [9606]"'''
)
ft_type = "motif"
ft_description = "9aaTAD"
ft_min_length = 10
ft_max_length = "*"
and_query = "(organism_id:9606)"
accessions_with_feature_type_and_length = get_accessions_with_feature_type_and_length(
    ft_type, ft_description, ft_min_length, ft_max_length, and_query
)
print(accessions_with_feature_type_and_length)
