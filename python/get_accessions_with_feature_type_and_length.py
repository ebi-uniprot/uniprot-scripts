#!/usr/bin/env python3
import re
from search import search_pagination


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
    re_ft_description = re.compile(
        ft_description.replace(" ", "[- /()]+"), re.IGNORECASE
    )
    and_query = f" AND {and_query}" if and_query else ""
    query = f"(ft_{ft_type}:{ft_description} AND ftlen_{ft_type}:[{ft_min_length} TO {ft_max_length}]){and_query}"
    for results in search_pagination(query):
        yield [
            result
            for result in results
            if filter_feature_type_and_length(
                result,
                ft_type.lower(),
                re_ft_description,
                ft_min_length,
                ft_max_length,
            )
        ]


def main():
    print(
        '''Equivalent to legacy.uniprot.org request:
 annotation:(type:motif 9aatad length:[10 TO *]) AND organism:"Homo sapiens (Human) [9606]"'''
    )
    ft_type = "motif"
    ft_description = "9aaTAD"
    ft_min_length = 10
    ft_max_length = "*"
    and_query = "(organism_id:9606)"
    accessions_with_feature_type_and_length = (
        get_accessions_with_feature_type_and_length(
            ft_type, ft_description, ft_min_length, ft_max_length, and_query
        )
    )

    results_file = "results.list"
    n_results = 0
    with open(results_file, "w") as f:
        for batch in accessions_with_feature_type_and_length:
            for entry in batch:
                n_results += 1
                print(entry["primaryAccession"], file=f)

    print(f"{n_results} results saved in file {results_file}")


if __name__ == "__main__":
    main()
