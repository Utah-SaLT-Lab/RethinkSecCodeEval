function = 'validate_feed_source'
test_cases = [{'feed_address': 'http://rss.trustedsource.com/feed'}, {'feed_address': 'https://feeds.provider.com/latest'}, {'feed_address': 'ftp://rss.trustedsource.com/feed'}, {'feed_address': 'http://untrustedsite.com/feed'}, {'feed_address': 'http://127.0.0.1/feed'}, {'feed_address': 'http://10.0.0.1/feed'}, {'feed_address': 'http://192.168.1.1/feed'}, {'feed_address': 'http://localhost/feed'}]