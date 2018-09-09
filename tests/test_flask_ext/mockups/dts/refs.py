from ...util import normalize_uri_string

phi1294_response = {
    "@context": {
        "hydra": "https://www.w3.org/ns/hydra/core#",
        "@vocab": "https://w3id.org/dts/api#",
    },
    "@id": normalize_uri_string("/dts/navigation?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2&groupBy=1&level=1"),
    "citeDepth": 3,
    "level": 1,
    "citeType": "book",
    "hydra:member": [
        {"ref": "1"},
        {"ref": "2"},
        {"ref": "3"},
        {"ref": "4"},
        {"ref": "5"},
        {"ref": "6"},
        {"ref": "7"},
        {"ref": "8"},
        {"ref": "9"},
        {"ref": "10"},
        {"ref": "11"},
        {"ref": "12"},
        {"ref": "13"},
        {"ref": "14"}
    ],
    "passage": normalize_uri_string("/dts/document"
                                        "?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2{&ref}{&start}{&end}")
}

phi1294_group_by_response = {
    "@context": {
        "hydra": "https://www.w3.org/ns/hydra/core#",
        "@vocab": "https://w3id.org/dts/api#",
    },
    "@id": normalize_uri_string("/dts/navigation?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2&groupBy=2&level=1"),
    "citeDepth": 3,
    "level": 1,
    "citeType": "book",
    "hydra:member": [{'end': '2', 'start': '1'},
               {'end': '4', 'start': '3'},
               {'end': '6', 'start': '5'},
               {'end': '8', 'start': '7'},
               {'end': '10', 'start': '9'},
               {'end': '12', 'start': '11'},
               {'end': '14', 'start': '13'}],
    "passage": normalize_uri_string("/dts/document"
                                        "?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2{&ref}{&start}{&end}")
}

phi1294_group_by_response_start_end = {
    "@context": {
        "hydra": "https://www.w3.org/ns/hydra/core#",
        "@vocab": "https://w3id.org/dts/api#",
    },
    "@id": normalize_uri_string("/dts/navigation?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2"
                                "&groupBy=100"
                                "&level=1"
                                "&start=1&end=2"),
    "citeDepth": 3,
    "level": 2,
    "citeType": "poem",
    "hydra:member": [
        {'end': '1.99', 'start': '1.pr'},
        {'end': '1.118', 'start': '1.100'},
        {'end': '2.93', 'start': '2.pr'}
    ],
    "passage": normalize_uri_string("/dts/document"
                                        "?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2{&ref}{&start}{&end}")
}

phi1294_group_by_response_ref_level_2 = {
    "@context": {
        "hydra": "https://www.w3.org/ns/hydra/core#",
        "@vocab": "https://w3id.org/dts/api#",
    },
    "@id": normalize_uri_string("/dts/navigation?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2"
                                "&groupBy=100"
                                "&level=2"
                                "&ref=1"),
    "citeDepth": 3,
    "level": 3,
    "citeType": "line",
    "hydra:member": [{'start': '1.pr.1', 'end': '1.pr.22'}, {'start': '1.1.1', 'end': '1.1.6'},
               {'start': '1.2.1', 'end': '1.2.8'}, {'start': '1.3.1', 'end': '1.3.12'},
               {'start': '1.4.1', 'end': '1.4.8'}, {'start': '1.5.1', 'end': '1.5.2'},
               {'start': '1.6.1', 'end': '1.6.6'}, {'start': '1.7.1', 'end': '1.7.5'},
               {'start': '1.8.1', 'end': '1.8.6'}, {'start': '1.9.1', 'end': '1.9.2'},
               {'start': '1.10.1', 'end': '1.10.4'}, {'start': '1.11.1', 'end': '1.11.4'},
               {'start': '1.12.1', 'end': '1.12.12'}, {'start': '1.13.1', 'end': '1.13.4'},
               {'start': '1.14.1', 'end': '1.14.6'}, {'start': '1.15.1', 'end': '1.15.12'},
               {'start': '1.16.1', 'end': '1.16.2'}, {'start': '1.17.1', 'end': '1.17.3'},
               {'start': '1.18.1', 'end': '1.18.8'}, {'start': '1.19.1', 'end': '1.19.4'},
               {'start': '1.20.1', 'end': '1.20.4'}, {'start': '1.21.1', 'end': '1.21.8'},
               {'start': '1.22.1', 'end': '1.22.6'}, {'start': '1.23.1', 'end': '1.23.4'},
               {'start': '1.24.1', 'end': '1.24.4'}, {'start': '1.25.1', 'end': '1.25.8'},
               {'start': '1.26.1', 'end': '1.26.10'}, {'start': '1.27.1', 'end': '1.27.7'},
               {'start': '1.28.1', 'end': '1.28.2'}, {'start': '1.29.1', 'end': '1.29.4'},
               {'start': '1.30.1', 'end': '1.30.2'}, {'start': '1.31.1', 'end': '1.31.8'},
               {'start': '1.32.1', 'end': '1.32.2'}, {'start': '1.33.1', 'end': '1.33.4'},
               {'start': '1.34.1', 'end': '1.34.10'}, {'start': '1.35.1', 'end': '1.35.15'},
               {'start': '1.36.1', 'end': '1.36.6'}, {'start': '1.37.1', 'end': '1.37.2'},
               {'start': '1.38.1', 'end': '1.38.2'}, {'start': '1.39.1', 'end': '1.39.8'},
               {'start': '1.40.1', 'end': '1.40.2'}, {'start': '1.41.1', 'end': '1.41.20'},
               {'start': '1.42.1', 'end': '1.42.6'}, {'start': '1.43.1', 'end': '1.43.14'},
               {'start': '1.44.1', 'end': '1.44.4'}, {'start': '1.45.1', 'end': '1.45.2'},
               {'start': '1.46.1', 'end': '1.46.4'}, {'start': '1.47.1', 'end': '1.47.2'},
               {'start': '1.48.1', 'end': '1.48.8'}, {'start': '1.49.1', 'end': '1.49.42'},
               {'start': '1.50.1', 'end': '1.50.2'}, {'start': '1.51.1', 'end': '1.51.6'},
               {'start': '1.52.1', 'end': '1.52.9'}, {'start': '1.53.1', 'end': '1.53.12'},
               {'start': '1.54.1', 'end': '1.54.7'}, {'start': '1.55.1', 'end': '1.55.14'},
               {'start': '1.56.1', 'end': '1.56.2'}, {'start': '1.57.1', 'end': '1.57.4'},
               {'start': '1.58.1', 'end': '1.58.6'}, {'start': '1.59.1', 'end': '1.59.4'},
               {'start': '1.60.1', 'end': '1.60.6'}, {'start': '1.61.1', 'end': '1.61.12'},
               {'start': '1.62.1', 'end': '1.62.6'}, {'start': '1.63.1', 'end': '1.63.2'},
               {'start': '1.64.1', 'end': '1.64.4'}, {'start': '1.65.1', 'end': '1.65.4'},
               {'start': '1.66.1', 'end': '1.66.14'}, {'start': '1.67.1', 'end': '1.67.2'},
               {'start': '1.68.1', 'end': '1.68.8'}, {'start': '1.69.1', 'end': '1.69.2'},
               {'start': '1.70.1', 'end': '1.70.18'}, {'start': '1.71.1', 'end': '1.71.4'},
               {'start': '1.72.1', 'end': '1.72.8'}, {'start': '1.73.1', 'end': '1.73.4'},
               {'start': '1.74.1', 'end': '1.74.2'}, {'start': '1.75.1', 'end': '1.75.2'},
               {'start': '1.76.1', 'end': '1.76.14'}, {'start': '1.77.1', 'end': '1.77.6'},
               {'start': '1.78.1', 'end': '1.78.10'}, {'start': '1.79.1', 'end': '1.79.4'},
               {'start': '1.80.1', 'end': '1.80.2'}, {'start': '1.81.1', 'end': '1.81.2'},
               {'start': '1.82.1', 'end': '1.82.11'}, {'start': '1.83.1', 'end': '1.83.2'},
               {'start': '1.84.1', 'end': '1.84.5'}, {'start': '1.85.1', 'end': '1.85.8'},
               {'start': '1.86.1', 'end': '1.86.13'}, {'start': '1.87.1', 'end': '1.87.8'},
               {'start': '1.88.1', 'end': '1.88.10'}, {'start': '1.89.1', 'end': '1.89.6'},
               {'start': '1.90.1', 'end': '1.90.10'}, {'start': '1.91.1', 'end': '1.91.2'},
               {'start': '1.92.1', 'end': '1.92.14'}, {'start': '1.93.1', 'end': '1.93.6'},
               {'start': '1.94.1', 'end': '1.94.2'}, {'start': '1.95.1', 'end': '1.95.2'},
               {'start': '1.96.1', 'end': '1.96.14'}, {'start': '1.97.1', 'end': '1.97.4'},
               {'start': '1.98.1', 'end': '1.98.2'}, {'start': '1.99.1', 'end': '1.99.18'},
               {'start': '1.100.1', 'end': '1.100.2'}, {'start': '1.101.1', 'end': '1.101.10'},
               {'start': '1.102.1', 'end': '1.102.2'}, {'start': '1.103.1', 'end': '1.103.12'},
               {'start': '1.104.1', 'end': '1.104.22'}, {'start': '1.105.1', 'end': '1.105.4'},
               {'start': '1.106.1', 'end': '1.106.10'}, {'start': '1.107.1', 'end': '1.107.8'},
               {'start': '1.108.1', 'end': '1.108.10'}, {'start': '1.109.1', 'end': '1.109.23'},
               {'start': '1.110.1', 'end': '1.110.2'}, {'start': '1.111.1', 'end': '1.111.4'},
               {'start': '1.112.1', 'end': '1.112.2'}, {'start': '1.113.1', 'end': '1.113.6'},
               {'start': '1.114.1', 'end': '1.114.6'}, {'start': '1.115.1', 'end': '1.115.7'},
               {'start': '1.116.1', 'end': '1.116.6'}, {'start': '1.117.1', 'end': '1.117.18'},
               {'start': '1.118.1', 'end': '1.118.2'}],
    "passage": normalize_uri_string("/dts/document"
                                        "?id=urn:cts:latinLit:phi1294.phi002.perseus-lat2{&ref}{&start}{&end}")
}
