"""Bounded plain-text artist metadata; no network or playback capabilities."""
from html.parser import HTMLParser


class BiographyText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.hidden = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
        elif tag in ('p', 'br', 'div', 'li'): self.parts.append(' ')

    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden = max(0, self.hidden - 1)
        elif tag in ('p', 'div', 'li'): self.parts.append(' ')

    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


def plain_biography(value):
    if not isinstance(value, str): return None
    parser = BiographyText()
    parser.feed(value[:32768])
    text = ' '.join(''.join(parser.parts).split())[:2000]
    return text or None
