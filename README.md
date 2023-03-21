# pss-json
script to rebuild the pss json

Reindexing PSS documents to Elasticsearch

Run the `pss-json-export.py` script against all sets (contents of ./data/)

Create a new index with filterable fields for keyword and time period values
```
curl -XPUT http://[ES_NODE]:9200/[INDEX]\?pretty -H "Content-Type: application/json" -d '
{
    "mappings":
    {
        "properties":
        {
            "about":
            {
                "type": "object",
                "properties":
                {
                    "disambiguatingDescription":
                    {
                        "type": "keyword",
                        "fields":
                        {
                            "not_analyzed":
                            {
                                "type": "keyword"
                            }
                        }
                    },
                    "name":
                    {
                        "type": "keyword",
                        "fields":
                        {
                            "not_analyzed":
                            {
                                "type": "keyword"
                            }
                        }
                    }
                }
            }
        }
    }
}'
```

Index updated documents from the ./sets/ directory (updated+[set name].json) 
```
find . -name "*updated_*.json" -type f | xargs -I{} sh -c 'echo "$1" "./$(basename ${1%.*}).${1##*.}"' -- {} | xargs -n 2 -P 8 sh -c 'curl -XPOST http://ES_NODE:9200/[INDEX]/doc -H "Content-Type: application/json" -d @"$0"'
```

Flop the alias to the new index
```
curl -XPOST http://[ES_NODE]:9200/_aliases -H 'Content-Type: application/json' -d '{"actions":[{"remove" : {"index" : "*", "alias" : "dpla_pss"}},{"add" : { "index" : "[INDEX]", "alias" : "dpla_pss" }}]}'
```

Test the indexing by getting the facet values for Time Period and Subject filters/facets/dropdowns 
```
curl -XGET http://[NODE]:9200/dpla_pss/_search\?pretty -H "Content-Type: application/json" \
-d '{
    "size": "1",
    "_source":
    {
        "includes":
        [
            "about.disambiguatingDescription", "about.name"
        ],
        "excludes":
        []
    },
    "query":
    {
        "match_all":
        {}
    },
    "aggs":
    {
        "disambiguatingDescriptionAgg":
        {
            "terms":
            {
                "field": "about.disambiguatingDescription"
            }
        }, "nameAgg":
        {
            "terms":
            {
                "field": "about.name"
            }
        }

    }
}'
```

Test sorting by dateCreated chronologically
```
curl -XGET http://[NODE]:9200/dpla_pss/_search\?pretty -H "Content-Type: application/json" \
-d '{
    "size": "500",
    "_source":
    {
        "includes":
        [
            "dateCreated", "name"
        ],
        "excludes":
        []
    },
    "query":
    {
        "match_all":
        {}
    },
    "sort" : [
        { "dateCreated" : {"order" : "desc"}}
    ]
}'
```
