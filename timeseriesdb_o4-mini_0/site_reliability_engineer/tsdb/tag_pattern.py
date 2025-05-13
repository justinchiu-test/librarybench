import re

class TagPatternQuery:
    @staticmethod
    def _pattern_to_regex(pat):
        # convert glob to regex
        pat = re.escape(pat)
        pat = pat.replace(r'\*', '.*').replace(r'\?', '.')
        return '^' + pat + '$'

    @staticmethod
    def query(tsdb, pattern):
        key, pat = pattern.split(':', 1)
        regex = re.compile(TagPatternQuery._pattern_to_regex(pat))
        results = []
        for series_key in tsdb.storage:
            # series_key is (name, frozenset_of_tag_items)
            tags_frozen = series_key[1]
            tags = dict(tags_frozen)
            if key in tags and regex.match(tags[key]):
                results.append(series_key)
        return results
