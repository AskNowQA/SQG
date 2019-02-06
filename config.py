config = {
    'general': {
        'http': {
            'timeout': 120
        },
        'dbpedia': {
            'endpoint': 'http://dbpedia.org/sparql',
            # 'endpoint': 'http://sda-srv01.iai.uni-bonn.de:8164/sparql',
            'one_hop_bloom_file': './data/blooms/spo1.bloom',
            'two_hop_bloom_file': './data/blooms/spo2.bloom'
        }
    }
}
