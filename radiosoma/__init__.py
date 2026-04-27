from collections import defaultdict
from xml.etree import cElementTree as ET

import requests


def _etree2dict(t):
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(_etree2dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update((k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['text'] = text
        else:
            d[t.tag] = text
    return d


def _xml2dict(xml_string):
    try:
        xml_string = xml_string.replace('xmlns="http://www.w3.org/1999/xhtml"', "")
        e = ET.XML(xml_string)
        return _etree2dict(e)
    except Exception:
        return {}


class SomaFmStation:
    def __init__(self, raw):
        self.raw = raw

    @property
    def station_id(self):
        return self.raw.get("id")

    @property
    def title(self):
        return self.raw.get("title") or self.raw.get("id")

    @property
    def image(self):
        return self.raw.get("xlimage") or \
               self.raw.get("largeimage") or \
               self.raw.get("image")

    @property
    def description(self):
        return self.raw.get("description", "")

    @property
    def genre(self):
        return self.raw.get("genre")

    @property
    def streams(self):
        streams = []
        for stream in self.raw.get("fastpls", []):
            try:
                streams.append(stream["text"])
            except (KeyError, TypeError):
                continue
        for stream in self.raw.get("highestpls", []):
            try:
                streams.append(stream["text"])
            except (KeyError, TypeError):
                continue
        return streams

    @property
    def best_stream(self):
        for stream in self.raw.get("highestpls", []):
            try:
                return stream["text"]
            except (KeyError, TypeError):
                continue
        for stream in self.raw.get("fastpls", []):
            try:
                return stream["text"]
            except (KeyError, TypeError):
                continue
        return None

    @property
    def fastest_stream(self):
        for stream in self.raw.get("fastpls", []):
            try:
                return stream["text"]
            except (KeyError, TypeError):
                continue
        for stream in self.raw.get("highestpls", []):
            try:
                return stream["text"]
            except (KeyError, TypeError):
                continue
        return None

    @property
    def m3u_stream(self):
        return f"http://somafm.com/m3u/{self.station_id}.m3u"

    @property
    def direct_stream(self):
        return f"http://ice2.somafm.com/{self.station_id}-128-mp3"

    @property
    def alt_direct_stream(self):
        return f"http://ice4.somafm.com/{self.station_id}-128-mp3"

    def __str__(self):
        return self.fastest_stream or ""

    def __repr__(self):
        return self.title + ":" + str(self)


def get_stations():
    xml = requests.get("https://api.somafm.com/channels.xml").text
    data = _xml2dict(xml)
    channels = data.get("channels", {}).get("channel", [])
    if isinstance(channels, dict):
        channels = [channels]
    for channel in channels:
        yield SomaFmStation(channel)
