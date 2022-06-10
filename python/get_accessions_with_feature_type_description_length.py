#!/usr/bin/env python3
import re
import argparse
from search import search_pagination


def filter_feature_type_description_length(
    result, ft_type, re_ft_description, ft_min_length, ft_max_length
):
    features = result["features"]
    for feature in features:
        if ft_type == feature["type"].lower() and (
            not re_ft_description or re_ft_description.search(feature["description"])
        ):
            start = feature["location"]["start"]["value"]
            end = feature["location"]["end"]["value"]
            length = end - start + 1
            if (ft_min_length == "*" or length >= ft_min_length) and (
                ft_max_length == "*" or length <= ft_max_length
            ):
                return True
    return False


def get_accessions_with_feature_type_description_length(
    ft_type, ft_description, ft_min_length, ft_max_length, and_query=None
):

    if ft_description == "*":
        re_ft_description = None
    else:
        re_ft_description = re.compile(
            ft_description.replace(" ", "[- /()]+"), re.IGNORECASE
        )
    if ft_min_length != "*":
        ft_min_length = int(ft_min_length)
    if ft_max_length != "*":
        ft_max_length = int(ft_max_length)
    and_query = f" AND {and_query}" if and_query else ""

    query = f"(ft_{ft_type}:{ft_description} AND ftlen_{ft_type}:[{ft_min_length} TO {ft_max_length}]){and_query}"
    for results in search_pagination(query, 50):
        yield [
            result
            for result in results
            if filter_feature_type_description_length(
                result,
                ft_type.lower(),
                re_ft_description,
                ft_min_length,
                ft_max_length,
            )
        ]


def main():
    parser = argparse.ArgumentParser(
        description="Query UniProtKB for features with type, description and length conditions all satisfied at the same time."
    )
    parser.add_argument("--ft_type", type=str)
    parser.add_argument("--ft_description", type=str, default="*")
    parser.add_argument("--ft_min_length", type=str, default="*")
    parser.add_argument("--ft_max_length", type=str, default="*")
    parser.add_argument("--and_query", type=str, default=None)
    parser.add_argument("--out", type=str, default="results.list")
    args = parser.parse_args()

    accessions_with_feature_type_and_length = (
        get_accessions_with_feature_type_description_length(
            args.ft_type,
            args.ft_description,
            args.ft_min_length,
            args.ft_max_length,
            args.and_query,
        )
    )

    n_results = 0
    with open(args.out, "w") as f:
        for batch in accessions_with_feature_type_and_length:
            for entry in batch:
                n_results += 1
                print(entry["primaryAccession"], file=f)

    print(f"{n_results} results saved in file {args.out}")


if __name__ == "__main__":
    main()
