class Post():
    def __init__(self,
                 url=None,
                 title=None,
                 section=None,
                 author=None,
                 pub_date=None,
                 tags=None,
                 hits=None,
                 shares=None,
                 thumb_urls=None,
                 metadata=None):
        self.url = url
        self.title = title
        self.section = section
        self.author = author
        self.pub_date = pub_date
        self.tags = tags
        self.hits = hits
        self.shares = shares
        self.thumb_urls = thumb_urls
        self.metadata = metadata

    @staticmethod
    def new_from_json_dict(data):
        return Post(url=data.get('url', None),
                    title=data.get('title', None),
                    section=data.get('section', None),
                    author=data.get('author', None),
                    pub_date=data.get('pub_date', None),
                    tags=data.get('tags', None),
                    hits=data.get('_hits', None),
                    shares=data.get('_shares', None),
                    metadata=data.get('metadata', None))


class Meta(object):
    def __init__(self, name=None, hits=None):
        self.name = name
        self.hits = hits


class Author(Meta):
    @staticmethod
    def new_from_json_dict(data):
        return Author(name=data.get('author', None),
                      hits=data.get('_hits', None))


class Section(Meta):
    @staticmethod
    def new_from_json_dict(data):
        return Section(name=data.get('section', None),
                       hits=data.get('_hits', None))


class Topic(Meta):
    @staticmethod
    def new_from_json_dict(data):
        return Topic(name=data.get('topic', None),
                     hits=data.get('_hits', None))


class Tag(Meta):
    @staticmethod
    def new_from_json_dict(data):
        return Tag(name=data.get('tag', None),
                   hits=data.get('_hits', None))


class Referrer(Meta):
    def __init__(self, name=None, hits=None, ref_type=None):
        super(Referrer, self).__init__(name=name, hits=hits)
        self.ref_type = ref_type

    @staticmethod
    def new_from_json_dict(data):
        return Referrer(name=data.get('tag', None),
                        hits=data.get('_hits', None),
                        ref_type=data.get('ref_type', data.get('type', None)))


class Shares():
    def __init__(self, tw=None, fb=None, pi=None, li=None, total=None):
        self.facebook = fb
        self.twitter = tw
        self.pinterest = pi
        self.linkedin = li
        self.total = total

    @staticmethod
    def new_from_json_dict(data):
        return Shares(tw=data.get('tw', None),
                      fb=data.get('fb', None),
                      pi=data.get('pi', None),
                      li=data.get('li', None),
                      total=data.get('total', None))
