default_app_config = 'mighty.apps.MightyConfig'

class VerifyException(Exception):
    def __init__(self, message):
        self.message = message

class Verify:
    def verify(self):
        for func in dir(self):
            if callable(getattr(self, func)) and func[0:7] == 'verify_':
                state = getattr(self, func)()
                if state: raise VerifyException(state)
        return True

stdtypes = {
    'numeric': [int, float, complex],
    'sequential': [list, tuple, range],
    'text': [str,],
    'mapping': [dict,]
}

units = {
    "currency": ["¤",  "&#164;",  "&curren;", ],
    "dollar":   ["$",  "&#36;",   "&dollar;", ],
    "cent":     ["¢",  "&#162;",  "&cent;",   ],
    "pound":    ["£",  "&#163;",  "&pound;",  ],
    "yen":      ["¥",  "&#165;",  "&yen;",    ],
    "euro":     ["€",  "&#8364;", "&euro;",   ],
    "colon":    ["₡",  "&#8353;", ],
    "naira":    ["₦",  "&#8358;", ],
    "rupee":    ["₨", "&#8360;", ],
    "won":      ["₩",  "&#8361;", ],
    "sheqel":   ["₪",  "&#8362;", ],
    "dong":     ["₫",  "&#8363;", ],
    "kip":      ["₭",  "&#8365;", ],
    "tugrik":   ["₮",  "&#8366;", ],
    "peso":     ["₱",  "&#8369;", ],
    "guarani":  ["₲",  "&#8370;", ],
    "hryvnia":  ["₴",  "&#8372;", ],
    "cedi":     ["₵",  "&#8373;", ],
    "tenge":    ["₸",  "&#8376;", ],
    "rupee":    ["₹",  "&#8377;", ],
    "lira":     ["₺",  "&#8378;", ],
    "manat":    ["₼",  "&#8380;", ],
    "ruble":    ["₽",  "&#8381;", ],
    "bitcoin":  ["₿",  "&#8383;", ],
}

mimetypes = [
    "application/EDI-X12",
    "application/EDIFACT",
    "application/javascript",
    "application/octet-stream",
    "application/ogg",
    "application/pdf",
    "application/xhtml+xml",
    "application/x-shockwave-flash",
    "application/json",
    "application/ld+json",
    "application/xml",
    "application/zip",
    "application/vnd.oasis.opendocument.text",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.graphics",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.mozilla.xul+xml",
    "audio/mpeg",
    "audio/x-ms-wma",
    "audio/vnd.rn-realaudio",
    "audio/x-wav",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/vnd.microsoft.icon",
    "image/vnd.djvu",
    "image/svg+xml",
    "multipart/mixed",
    "multipart/alternative",
    "multipart/related",
    "Type text",
    "text/css",
    "text/csv",
    "text/html",
    "text/javascript (obsolète)",
    "text/plain",
    "text/xml",
    "video/mpeg",
    "video/mp4",
    "video/quicktime",
    "video/x-ms-wmv",
    "video/x-msvideo",
    "video/x-flv",
    "video/web",
    "application/x-javascript",
]

exclude = ["je", "me", "moi", "tu", "te", "toi", "nous", "vous", "il", "elle",
    "ils", "elles", "se", "en", "y", "le", "la", "les", "lui", "soi", "leur", "eux",
    "lui", "leur", "celui", "celui-ci", "celui-la", "celle", "celle-ci", "celle-la",
    "ceux", "ceux-ci", "ceux-la", "celles", "celles-ci", "celles-la", "ce", "ceci", "cela", "ça",
    "mien", "tien", "sien", "mienne", "tienne", "sienne", "miens", "tiens", "siens", "miennes", "tiennes", "siennes",
    "notre", "votre", "leur", "notre", "votre", "leur", "notres", "votres", "leurs", "qui", "que", "quoi", "dont", "ou",
    "lequel", "auquel", "duquel", "laquelle", "a laquelle", "de laquelle", "lesquels", "auxquels", "desquels",
    "lesquelles", "auxquelles", "desquelles",
    "qui", "que", "quoi", "est-ce", "lequel", "auquel", "duquel", "laquelle", "a laquelle", "de laquelle",
    "lesquels", "auxquels", "desquels", "lesquelles", "auxquelles", "desquelles",
    "on", "tout", "un", "une", "les", "uns", "unes", "un autre", "une autre", "autres", "autre", "aucun", "aucune", "aucuns", "aucunes",
    "certains", "certaine", "certains", "certaines", "tel", "telle", "tels", "telles", "tout", "toute", "tous", "toutes",
    "même", "même", "mêmes", "nul", "nulle", "nuls", "nulles", "quelqu", "quelques uns", "quelques unes",
    "autrui", "quiconque", "mais", "donc", "or", "ni", "car", "cas", "avec", "sans", "pour", "contre", "malgré", "en", "par", "sur"]


"""
Make a file with the sql result in json
[clas] Config class to override
[conf] dict() contain the config to override
"""
def over_config(clas, conf):
    if conf:
        settable = stdtypes['mapping']+stdtypes['numeric']+stdtypes['text']+stdtypes['sequential']
        for key, val in conf.items():
            if hasattr(clas, key) and type(getattr(clas, key)) in settable:
                if type(getattr(clas, key)) in stdtypes['mapping']:
                    getattr(clas, key).update(val)
                else:
                    setattr(clas, key, val)
            elif type(getattr(clas, key)) == type:
                over_config(getattr(clas, key), val)
            else:
                setattr(clas, key, val)
