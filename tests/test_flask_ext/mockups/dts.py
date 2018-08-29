response_phi1294 = {
    '@context': {'ns1': 'http://www.w3.org/2004/02/skos/core#', 'cts': 'http://chs.harvard.edu/xmlns/cts/',
                           'dts': 'https://w3id.org/dts/api#', '@vocab': 'https://www.w3.org/ns/hydra/core#'},
    'title': 'Martial',
    'totalItems': 1,
    '@type': 'Collection',
    '@id': 'urn:cts:latinLit:phi1294',
    'dts:extensions': {
        'cts:groupname': [{'@value': 'Martial', '@language': 'eng'}],
        'ns1:prefLabel': [{'@value': 'Martial', '@language': 'eng'}]
    },
    'member': [
        {'title': 'Epigrammata', 'totalItems': 1, '@type': 'Collection', '@id': 'urn:cts:latinLit:phi1294.phi002'}
    ]
}

response_defaultTic = {
    '@type': 'Collection',
    '@context': {'@vocab': 'https://www.w3.org/ns/hydra/core#'},
    '@id': 'defaultTic',
    'title': 'None', 'totalItems': 1,
    'member': [
        {
            '@type': 'Collection',
            'totalItems': 2,
            '@id': 'default',
            'title': 'Default collection'
        }
    ]
}

response_phi1294_phi002_parent = {
    '@type': 'Collection',
    '@id': 'urn:cts:latinLit:phi1294.phi002',
    'title': 'Epigrammata',
    'totalItems': 1,
    'dts:extensions': {
        'ns2:prefLabel': [{'@language': 'eng', '@value': 'Epigrammata'}],
        'cts:title': [{'@language': 'eng', '@value': 'Epigrammata'}]
    },
    'member': [
        {
            'title': 'Martial',
            'totalItems': 1,
            '@type': 'Collection',
            '@id': 'urn:cts:latinLit:phi1294',
        }
    ],
    '@context': {
        'cts': 'http://chs.harvard.edu/xmlns/cts/',
        'ns2': 'http://www.w3.org/2004/02/skos/core#',
        'dts': 'https://w3id.org/dts/api#',
        '@vocab': 'https://www.w3.org/ns/hydra/core#'
    }
}
