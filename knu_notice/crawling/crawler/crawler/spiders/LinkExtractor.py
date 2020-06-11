from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.utils.python import unique as unique_list
from scrapy.utils.response import get_base_url

class MyLinkExtractor(LxmlLinkExtractor):
    def __init__(
        self,
        allow=(),
        deny=(),
        allow_domains=(),
        deny_domains=(),
        restrict_xpaths=(),
        tags=('a', 'area'),
        attrs=('href',),
        canonicalize=False,
        unique=True,
        process_value=None,
        deny_extensions=None,
        restrict_css=(),
        strip=True,
        restrict_text=None,
    ):
        super().__init__(
            allow,
            deny,
            allow_domains,
            deny_domains,
            restrict_xpaths,
            tags,
            attrs,
            canonicalize,
            unique,
            process_value,
            deny_extensions,
            restrict_css,
            strip,
            restrict_text,
        )

    # Override extract_links()
    def extract_links(self, response, omit=True):
        """Returns a list of :class:`~scrapy.link.Link` objects from the
        specified :class:`response <scrapy.http.Response>`.
        Only links that match the settings passed to the ``__init__`` method of
        the link extractor are returned.
        Duplicate links are omitted or not.
        """
        base_url = get_base_url(response)
        if self.restrict_xpaths:
            docs = [
                subdoc
                for x in self.restrict_xpaths
                for subdoc in response.xpath(x)
            ]
        else:
            docs = [response.selector]
        all_links = []
        for doc in docs:
            links = self._extract_links(doc, response.url, response.encoding, base_url)
            all_links.extend(self._process_links(links))
        if omit:
            return unique_list(all_links)
        else:
            return all_links