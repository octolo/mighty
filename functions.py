from django.apps import apps
from django.db.models import F, Func
from django.conf import settings
from django.core import serializers
from django.utils.module_loading import import_string
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from mighty.apps import MightyConfig as conf
from mighty import stdtypes, fields
from pathlib import Path
import base64, datetime, string, random, unicodedata, re, json, sys, subprocess, threading, requests

BS = conf.Crypto.BS
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[:-ord(s[len(s)-1:])]
numeric_const_pattern = "[-+]? (?: (?: \d* [\.,] \d+ ) | (?: \d+ [\.,]? ) )(?: [Ee] [+-]? \d+ ) ?"
drf_enable = 'rest_framework' in settings.INSTALLED_APPS
request_kept = threading.local()

# Request kept
def get_request_kept():
    return getattr(request_kept, 'request', None)

def get_descendant_value(path, obj):
    path = path.split('.')
    for p in path:
        obj = getattr(obj, p) if hasattr(obj, p) else False
    return obj

def batch_bulk_chunk(model, objects, chunk):
    schunk = 0
    while True:
        batch = objects[schunk:schunk+chunk]
        if not len(batch):
            break
        model.objects.bulk_create(objects)
        schunk+=chunk

"""
Round function for sql usage
"""
class Round(Func):
  function = "ROUND"
  arity = 2

"""
List of default tempates
"""
tpl = lambda a, n, t: [
    "%s/%s/%s.html" % (a, n, t),
    "%s/%s.html" % (n, t),
    "%s/%s.html" % (a, t),
    "%s.html" % t,]

"""
List of default templates AJAX
"""
tplx = lambda a, n, t: [
    "%s/%s/ajax/%s.html" % (a, n, t),
    "%s/ajax/%s.html" % (n, t),
    "ajax/%s.html" % t,]

"""
Shortcut to get a setting django
"""
def setting(name, default=None):
    return getattr(settings, name, default)

"""
Return True/False if input not in search list
[input_str] the data tested
[search] the list to tested the data
"""
def test(input_str=None, search=conf.Test.search, *args, **kwargs):
    if "positive" in kwargs and input_str in kwargs["positive"]: return True
    return True if str(input_str).strip().lower().replace(" ", "") not in search else False

def mask(inpt, start=2, limit=10):
    x = (len(str(inpt))-start)
    x = x if x <= limit else limit
    return str(inpt)[:start] + '*' * x

def masking_email(email):
    return re.sub(r'(?<=.)[^@](?=[^@]*?[^@]@)|(?:(?<=@.)|(?!^)(?=[^@]*$)).(?=.*[^@]\.)', "*", email, 0)

def masking_phone(phone):
    return re.sub(r'(?<=.....)(?=\d*)\d', '*', phone[:-1], 0)+phone[-1:]

"""
Return a data or none
"""
def get_or_none(data):
    return data if not test(data) else None

"""
Return a key
"""
def key(size=32, generator=string.hexdigits):
    return "".join(random.choice(generator) for x in range(size))

# Generate unique code for model
def generate_code(obj, *args, **kwargs):
    number = kwargs.get('number', '')
    params = kwargs.get('params', {})
    size = kwargs.get('size', 6)
    generator = kwargs.get('generator', string.ascii_uppercase+string.digits)
    params['code'] = kwargs.get('code', key(size, generator)) + number
    try:
        if obj.pk:
            type(obj).objects.exclude(pk=obj.pk).get(**params)
        else:
            type(obj).objects.get(**params)
        return generate_code(model, *args, **kwargs)
    except ObjectDoesNotExist:
        return code

"""
Return a code with the length used
"""
def randomcode(size=8):
    return key(size=size, generator="123456789")

"""
Cast input in float
"""
def make_float(flt):
    if test(flt):
        flt = re.compile(numeric_const_pattern, re.VERBOSE).search(flt).group().replace(",", ".")
        return float(flt)
    return None

"""
Cast input in integer
"""
def make_int(itg):
    if test(itg):
        return int(make_float(itg))
    return None

"""
Get and cast the string from the input
"""
def make_string(input_str):
    if ("," in input_str):
        input_str = re.sub(r"[^\w\s]"," ",input_str).strip()
        return input_str
    return re.sub(r"[^\w\s]"," ", input_str).strip()

"""
Return comments splitted from the input
"""
def split_comment(input_str):
    return re.search( "([\w\d'&,\. ]+)?\((.*)\)" , input_str)

"""
Return a tuple of backends
"""
def get_backends(backends_list, return_tuples=False, path_extend='', *args, **kwargs):
    backends = []
    for backend_path in backends_list:
        backend_path = backend_path + path_extend
        backend = import_string(backend_path)(*args, **kwargs)
        backends.append((backend, backend_path) if return_tuples else backend)
    if not backends:
        raise ImproperlyConfigured('No backends have been defined.')
    return backends

"""
Do a system command
"""
def command(cmd):
    out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    out = out.decode('utf-8')
    err = err.decode('utf-8')
    return err, out, cmd

"""
Return a service uptime by command system
"""
def service_uptime(service, cmd=None):
    err, out, cmd = command(cmd if cmd else conf.Service.uptime % service)
    try:
        out = float(out.strip())
    except Exception:
        out = 0
    return err, out, cmd


"""
Return a service cpu or memory usage by commande system
"""
def service_cpumem(cmd):
    err, out, cmd = command(cmd)
    if not err:
        out = out.strip().split('\n')
        load = round(sum([float(i) for i in out if len(i)]), 2)
        nb = len(out)
        return err, load, nb, cmd
    return err, out, 0, cmd

"""
Return a service cpu usage
"""
def service_cpu(service, cmd):
    return service_cpumem(cmd if cmd else conf.Service.cpu % service)

"""
Return a service memory usage
"""
def service_memory(service, cmd=None):
    return service_cpumem(cmd if cmd else conf.Service.memory % service)


# from Crypto import Cipher, Random
# """
# Return encrypted data with a key in base64 encoded
# [key] key used to encrypt raw
# [raw] string to encrypt
# """
# def encrypt(key, raw):
    # raw = pad(raw)
    # iv = Random.new().read(Cipher.AES.block_size)
    # _cipher = Cipher.AES.new(key, Cipher.AES.MODE_CFB, iv)
    # return base64.b64encode(iv+_cipher.encrypt(raw))

# """
# Decrypt data with a key
# [key] key to decrypt
# [enc] string base64 encoded
# """
# def decrypt(key, enc):
    # enc = base64.b64decode(enc)
    # iv = enc[:16]
    # _cipher = Cipher.AES.new(key, Cipher.AES.MODE_CFB, iv)
    # return unpad(_cipher.decrypt(enc[16:]))

"""
Return a model from a label and a model name
[label] label of the model
[model] name of the model
"""
def get_model(label, model):
    return apps.get_model(label, model)

"""
Get a model from a label and a model name
[reference] info about to get the model
"""
def input_get_model(reference):
    label = input("What label is for the reference %s: " % reference)
    model = input("What model is for the reference %s: " % reference)
    return get_model(label, model)

"""
Ask a boolean question
[question] the question
[default] answer default
"""
def boolean_input(question, default="n"):
    result = input("%s " % question)
    while len(result) < 1 or result[0].lower() not in "yn":
        result = input("Please answer yes(y) or no(n), default(%s): " % default)
    return result[0].lower() == "y"

"""
Ask to search in a model
[model] model to search
[reference] info about the search
"""
def object_search(model, reference):
    result = input("Make a search that refers to %s (keep empty for pass): " % reference)
    if test(result):
        objects_list = model.objects.filter(search__contains=make_searchable(result))
        return multipleobjects_onechoice(objects_list, reference, model)
    return None

"""
Ask for choice a model if multiple objects was return
[objects_list] list of objects
[reference] info to get the list
[model] model expected
"""
def multipleobjects_onechoice(objects_list, reference, model):
    objects = [None, ]
    i = 0
    print("0. for search")
    for obj in objects_list:
        i += 1
        objects.append(obj)
        print("%s. %s (%s)" % (i, str(obj), obj.id))
    result = input("choose the object that refers to %s (keep empty for pass): " % reference)
    if test(result):
        choice = make_int(result)
        if choice == 0:
            return object_search(model, reference)
        else:
            return objects[choice]
    return None

"""
Return model from a foreignkey
[model] Model contain the foreignkey
[field] Field of the foreignkey
[data] Value of the foreignkey
[ret] Attribute to return
"""
def foreignkey_from(model, field, data, ret):
    return getattr(model.objects.get(**{field: data}), ret)

"""
Make a string searchable
"""
def searchable(input_str):
    for i in conf.Test.replace:
        input_str = input_str.replace(i, " ")
    input_str = re.sub(" +", " ", input_str)
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def format_non_alpha(text):
    for ch in ['\\','`','*','_','{','}','[',']','(',')','>','#','+','-','.','!','$','\'']:
        if ch in text:
            text = text.replace(ch, "-")
    return text

def make_searchable(input_str):
    return searchable(input_str).lower()

"""
Return differences between 2 models
you can exclude some field with arg [exclude]
"""
def models_difference(first, second, exclude=fields.base):
    nfirst, nsecond = {}, {}
    for field in first.fields():
        if field not in exclude and getattr(first, field) != getattr(second, field):
            nfirst[field] = getattr(first, field)
            nsecond[field] = getattr(second, field)
    return nfirst, nsecond

"""
Make a directory of image by date and content type
/contenttype/year/month/{uid,id}/image
"""
def image_directory_path(instance, filename):
    directory = str(instance.__class__.__name__).lower()
    date = datetime.datetime.now()
    ext = filename.split(".")[-1:]
    if hasattr(instance, "uid"):
        return "{0}/{1}/{2}/{3}.{4}".format(directory, date.year, date.month, instance.uid, ext)
    else:
        return "{0}/{1}/{2}/{3}.{4}".format(directory, date.year, date.month, instance.id, ext)

"""
Make a directory of file by date and content type
/contenttype/year/month/{uid,id}/file
"""
def file_directory_path(instance, filename, directory=None):
    if not directory: directory = str(instance.__class__.__name__).lower()
    date = datetime.datetime.now()
    if hasattr(instance, "parent"):
        selfpath = instance.parent.uid if hasattr(instance.parent, 'uid') and instance.parent.uid else instance.parent.id
        return "%s/%s/%s/%s/%s" % (directory, date.year, date.month, selfpath, filename)
    elif hasattr(instance, 'fieldparent') and hasattr(instance, instance.fieldparent):
        parent = getattr(instance, instance.fieldparent)
        selfpath = parent.uid if hasattr(parent, 'uid') and parent.uid else parent.id
        return "%s/%s/%s/%s/%s" % (directory, date.year, date.month, selfpath, filename)
    selfpath = instance.uid if hasattr(instance, 'uid') and instance.uid else instance.id
    return "%s/%s/%s/%s/%s" % (directory, date.year, date.month, selfpath, filename)

"""
same as file_directory_path but start with cloudstorage/
cloudstorage/contenttype/year/month/{uid,id}/file
"""
def cloud_directory_path(instance, filename):
    file_directory_path(instance, filename, conf.Directory.cloud)

"""
Return a score of similarity out of 100 between two strings
"""
# String score
def similar_str(str1, str2):
    max_len = tmp = pos1 = pos2 = 0
    len1, len2 = len(str1), len(str2)
    for p in range(len1):
        for q in range(len2):
            tmp = 0
            while p + tmp < len1 and q + tmp < len2 \
                    and str1[p + tmp] == str2[q + tmp]:
                tmp += 1
            if tmp > max_len:
                max_len, pos1, pos2 = tmp, p, q
    return max_len, pos1, pos2

# Char score
def similar_char(str1, str2):
    max_len, pos1, pos2 = similar_str(str1, str2)
    total = max_len
    if max_len != 0:
        if pos1 and pos2:
            total += similar_char(str1[:pos1], str2[:pos2])
        if pos1 + max_len < len(str1) and pos2 + max_len < len(str2):
            total += similar_char(str1[pos1 + max_len:], str2[pos2 + max_len:]);
    return total

# Get the score
def similar_text(str1, str2):
    if not (isinstance(str1, str) or isinstance(str1, unicode)):
        raise TypeError("must be str or unicode")
    elif not (isinstance(str2, str) or isinstance(str2, unicode)):
        raise TypeError("must be str or unicode")
    elif len(str1) == 0 and len(str2) == 0:
        return 0.0
    else:
        return int(similar_char(str1, str2) * 200.0 / (len(str1) + len(str2)))

"""
Return an array of words rarely found in an input
[input_str] the text where search
[exclude] list of words to exclude to the search
- optionals
-- [split] split regex
-- [weight] size of minimal weight
"""
def weight_words(input_str, exclude=conf.exclude, *args, **kwargs):
    split  = kwargs["split"] if "split" in kwargs else "[^\w]"
    weight  = kwargs["weight"] if "weight" in kwargs else 3
    words = []
    input_split = re.sub(split, " ",  input_str).split()
    for word in input_split:
        word = make_searchable(word)
        if len(word) > weight and word not in words and word not in exclude:
            words.append(word)
    return words

"""
Get a file json and return datas loaded
"""
def get_jsonfile(fil):
    if Path(fil).is_file():
        with open(fil) as json_file:
            return json.load(json_file)
    return False

"""
Make a json file with datas
[datas] json datas to write
[fil] the file name (.json if possible)
[tmp] the path file
"""
def to_jsonfile(datas, fil, tmp="/tmp/"):
    with open(tmp + fil, "w") as f:
        json.dump(datas, f, ensure_ascii=False, indent=4)

"""
Make a file with the sql result in json
[sql] the query sql
[fil] the file name (.json if possible)
[tmp] the path file
"""
def sql_to_jsonfile(sql, fil, tmp="/tmp/"):
    to_jsonfile(sql, fil, tmp)

"""
Return the logger set
"""
def get_logger():
    if hasattr(settings, 'LOGGER_BACKEND'):
        return import_string(settings.LOGGER_BACKEND)()
    else:
        import logging
        logger = logging.getLogger(__name__)
        return logger

"""
Return data in binary format
"""
def to_binary(data):
    return ' '.join(format(x, 'b') for x in bytearray(data, 'utf-8'))

"""
Return a form dynamically created
"""
def get_form(**kwargs):
    form_class = kwargs.get('form_class', forms.Form)
    form_fields = kwargs.get('form_fields', [])
    class DynForm(form_class):
        class Meta:
            fields = fields
    return DynForm

"""
Return a form model dynamically created
"""
def get_form_model(model_class, **kwargs):
    form_class = kwargs.get('form_class', forms.ModelForm)
    form_fields = kwargs.get('form_fields', [])
    class DynForm(form_class):
        class Meta:
            model = model_class
            fields = form_fields
    return DynForm

def calcul_size(size, unit):
    return round(float(size/conf.FileSystem.units_mapping[unit][0]), 2)

def human_size(size):
    for unit, config in conf.FileSystem.units_mapping.items():
        if size >= config[0]: break
    return unit, calcul_size(size, unit)

def pretty_size(size, unit=None):
    if not unit: return human_size(size)
    return unit, calcul_size(size, unit)

def pretty_long(size, unit):
    unit = conf.FileSystem.units_mapping[unit][1] if size > 1 else conf.FileSystem.units_mapping[unit][2]
    return conf.FileSystem.unit % (str(size), unit)

def pretty_size_long(size, unit=None):
    unit, size = pretty_size(size, unit)
    return pretty_long(size, unit)

def pretty_size_short(size, unit=None):
    unit, size = pretty_size(size, unit)
    return conf.FileSystem.unit % (str(size), unit)

def scrap_xpath(xpath, *args, **kwargs):
    from lxml import html
    content = kwargs.get("content")
    url = kwargs.get("url")
    content = requests.get(url).content if url else content
    content = html.fromstring(content)
    return content.xpath(xpath)

def url_json_data(url):
    try:
        response = requests.get(url)
        if 200 <= response.status_code <= 300:
            return response.json()
    except Exception:
        pass
    return False