# Requirements

Python 3

# Installation

```
git clone https://github.com/ebi-uniprot/uniprot-scripts.git
cd uniprot-scripts
pip3 install requests
```

# Python scripts

## get_accessions_with_feature_type_and_length.py

This script can be used from the command line as seen in the following example:

```
./python/get_accessions_with_feature_type_and_length.py \
--ft_type "motif" \
--ft_description "9aaTAD" \
--ft_min_length 10 \
--ft_max_length "*" \
--and_query "(organism_id:9606)" \
--out results.list
```

The saved results can then be used as part of a Retrieve/ID mapping query to retreive additional data (eg FASTA, TSV, JSON)

## search.py

You can use `search.py` as a template for writing your own scripts or just modify the `main()` function with your own parameters. This file contains two different ways to perform a search: pagination and streaming:

```
search_pagination(query, size=100, namespace="uniprotkb")
```

This way of searching uses the `search` endpoint which retrieves the results in batches. This can be useful when you expect the query to be large and you want to apply some function on each batch as it arrives.

```
search_stream(query, namespace="uniprotkb")
```

This way of searching used the `stream` endpoint which fetches everything at once. This can be useful if you just want all of the result at once. If there is a disruption in your connection this will mean you will need to restart the stream search so `search` can be more robust in this respect.
