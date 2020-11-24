'''Module for getting metadata about repository. (generated data about cached data)'''
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional, Set
from pathlib import Path
import time
import bs4
import humanize
from jinja2 import Markup
import re
import functools

from scripts.minfmt import ignore_sbrack
from scripts.caching.ghrepo import repos_cached
from scripts.config import gh
from scripts import Mod

def fix_image_url(url, repo_name):
    '''Fixes a GitHub image urls.

    Any links with `github.com` are invalid, because the return *html*
    content. Image links would have `githubusercontent.com`. For example:

    - This returns an html: https://github.com/Retrothopter/Niobium-Nanotech/blob/master/Preview.png
    - This returns a png: https://githubusercontent.com/Retrothopter/Niobium-Nanotech/blob/master/Preview.png

    Any links that are relative are also invalid. For example:

    - preview.png
    - sprites/preview.png
    - /sprites/preview.png'''
    from urllib.parse import urlparse
    from parsec import optional, string, regex, none_of, many, ParseError

    glob = (optional(string('/'))
            >> string(repo_name)
            >> string("/blob/master/")
            >> many(none_of("?")).parsecmap(lambda x: "".join(x)))

    o = urlparse(url)
    if o.netloc == "raw.githubusercontent.com":
        return url

    try:
        path = glob.parse(o.path)
    except ParseError as e:
        path = None
    if o.netloc == "github.com" and path:
        return f"https://raw.githubusercontent.com/{repo_name}/master/{path}"

    if o.netloc == "":
        return f"https://raw.githubusercontent.com/{repo_name}/master/{o.path}"

    return url

def fix_urls(md, repo_name):
    def on_match(link):
        desc = link.group(1)
        old = link.group(2)
        href = fix_image_url(link.group(2), repo_name)
        old, new = f'[{desc}]({old})', f'[{desc}]({href})'
        if repo_name == "AeronGreva/AeroMindustry":
            print(old, new)
        return old, new

    replacers = set((on_match(x) for x in re.finditer(r'\[([^\]\[]*)\]\(([^\)]*)\)', md)))
    return functools.reduce(lambda md, x: md.replace(x[0], x[1]), replacers, md)

class ModMeta:
    '''The front for the various data cachers. Handles special cases that 
    don't specifically need to be cached or know about each other.'''

    def __repr__(self):
        return f"ModMeta(name=\"{self.name}\", date=\"{self.date}\")"

    def _header(self):
        from markdown import markdown

        html = markdown(self.readme)
        soup = bs4.BeautifulSoup(html, 'html.parser')
        links = soup.find_all('img')
        links = [ fix_image_url(l['src'], self.repo) for l in links ]
        if links:
            return links[0]
        else:
            return ''

    @staticmethod
    def build(repo_obj, icon):
        def parse_or_nothing(x):
            return ignore_sbrack.parse(x or "")

        r = repo_obj
        mods_name = parse_or_nothing(r.mod.name) if r.mod.name else r.name
        mods_desc = parse_or_nothing(r.mod.description)
        author = parse_or_nothing(r.mod.author)
        mindustry_name = r.name.split("/")[1].lower().replace(" ", "-")

        return Mod(
            name=mods_name,
            name_markup=r.mod.displayName or r.mod.name,
            link=f"https://github.com/{r.name}",
            repo=r.name,
            desc=mods_desc,
            desc_markup=r.mod.description,
            icon=icon,
            stars=r.stars,
            author=author.strip(),
            author_markup=r.mod.author,
            date=str(r.date),
            date_tt=time.mktime(r.date.timetuple()),
            readme=fix_urls(r.readme or '', r.name),
            version=r.mod.version,
            assets=list(r.assets),
            contents=list(r.contents),
            display_name=r.mod.displayName,
        )

    @staticmethod
    def builds(repo_objs, icons):
        return [ ModMeta.build(x, icons[x.name])
                 for x in repo_objs ]

    def into_mod(self):
        return Mod(**self.pack_data())
