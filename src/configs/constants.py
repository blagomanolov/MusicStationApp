from typing import Dict, Iterable, Set
import re

BRACKETS_RE: re.Pattern = re.compile(r"(\[[^\]]*\]|\([^\)]*\))")

SEPARATORS_RE: re.Pattern = re.compile(r"\s*(?:-|–|—|\||·|:|;)\s*")

GENERIC_WORDS: Set = {"radio", "fm", "@fm", "am", "live", "online", "station", "the", "hd"}

SPACES_RE: re.Pattern = re.compile(r"\s+")

GENRE_SYNONYMS: Dict[str, Iterable[str]] = {
    "pop": ["pop", "top40", "top 40", "hits", "chart"],
    "rock": ["rock", "alt rock", "alternative", "indie rock", "classic rock", "hard rock"],
    "metal": ["metal", "heavy metal", "death metal", "black metal", "power metal"],
    "house": ["house", "deep house", "tech house", "progressive house"],
    "techno": ["techno", "minimal techno", "detroit techno"],
    "trance": ["trance", "uplifting trance", "progressive trance"],
    "edm": ["edm", "electronic dance", "dance"],
    "hip hop": ["hiphop", "hip hop", "rap", "trap"],
    "rnb": ["rnb", "r&b", "rhythm and blues"],
    "jazz": ["jazz", "smooth jazz", "bebop", "swing"],
    "blues": ["blues", "delta blues"],
    "classical": ["classical", "symphony", "orchestra", "baroque", "romantic era"],
    "country": ["country", "bluegrass", "americana"],
    "reggae": ["reggae", "dancehall", "dub"],
    "latin": ["latin", "salsa", "bachata", "merengue", "reggaeton", "cumbia"],
    "k-pop": ["k-pop", "kpop"],
    "j-pop": ["j-pop", "jpop"],
    "punk": ["punk", "punk rock"],
    "alternative": ["alternative", "alt", "alt-pop", "alt rock"],
    "indie": ["indie", "indie pop", "indie rock"],
    "ambient": ["ambient", "chillout", "downtempo"],
    "lofi": ["lofi", "lo-fi", "lo fi"],
    "disco": ["disco"],
    "funk": ["funk", "boogie"],
    "soul": ["soul", "motown", "northern soul"],
    "gospel": ["gospel", "christian", "worship"],
    "news": ["news", "headline", "bulletin"],
    "talk": ["talk", "talkshow", "talk show"],
    "sports": ["sports", "sport", "football", "soccer", "baseball", "basketball"],
    "electronic": ["electronic", "electronica", "idm"],
    "drum and bass": ["drum and bass", "dnb", "drum & bass"],
    "dubstep": ["dubstep"],
    "afrobeat": ["afrobeat", "afrobeats", "afro beats"],
    "arabic": ["arabic", "tarab"],
    "bollywood": ["bollywood", "hindi", "desi"],
    "bhangra": ["bhangra"],
    "folk": ["folk", "celtic"],
    "acoustic": ["acoustic", "singer-songwriter"],
    "instrumental": ["instrumental"],
    "soundtrack": ["soundtrack", "ost", "film score"],
    "oldies": ["oldies", "retro", "gold"],
    "80s": ["80s", "80's"],
    "90s": ["90s", "90's"],
    "00s": ["00s", "2000s"],
    "world": ["world", "world music", "global"],
    "chill": ["chill", "chillout", "chill out"],
}