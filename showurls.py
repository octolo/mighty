import functools
import operator
import re

from django.conf import settings
from django.contrib.admindocs.views import simplify_regex
from django.core.exceptions import ViewDoesNotExist
from django.core.management import color
from django.core.management.base import CommandError
from django.urls import URLPattern, URLResolver  # type: ignore
from django.utils import translation


class RegexURLPattern:
    pass


class RegexURLResolver:
    pass


class LocaleRegexURLResolver:
    pass


def describe_pattern(p):
    return str(p.pattern)


def _dummy_style_func(msg):
    return msg


def no_style():
    style = color.no_style()
    for role in (
        'INFO',
        'WARN',
        'BOLD',
        'URL',
        'MODULE',
        'MODULE_NAME',
        'URL_NAME',
    ):
        setattr(style, role, _dummy_style_func)
    return style


FMTR = {
    'dense': '{url}\t{module}\t{url_name}\t{decorator}',
    'table': '{url},{module},{url_name},{decorator}',
    'aligned': '{url},{module},{url_name},{decorator}',
    'verbose': '{url}\n\tController: {module}\n\tURL Name: {url_name}\n\tDecorators: {decorator}\n',
    'json': '',
    'pretty-json': '',
}


class ShowUrls:
    help = 'Displays all of the url matching routes for the project.'

    def get_urls(self, *args, **options):
        options.get('style', no_style())
        options.get('unsorted', False)
        opt_language = options.get('language')
        opt_decorator = options.get('decorator', [])
        opt_format = options.get('format', 'dense')
        opt_urlconf = options.get('urlconf', 'ROOT_URLCONF')

        language = opt_language
        if language is not None:
            translation.activate(language)
            self.LANGUAGES = [
                (code, name)
                for code, name in getattr(settings, 'LANGUAGES', [])
                if code == language
            ]
        else:
            self.LANGUAGES = getattr(settings, 'LANGUAGES', ((None, None),))

        decorator = opt_decorator
        if not decorator:
            decorator = ['login_required']

        format_style = opt_format
        if format_style not in FMTR:
            raise CommandError(
                "Format style '{}' does not exist. Options: {}".format(
                    format_style,
                    ', '.join(sorted(FMTR.keys())),
                )
            )
        pretty_json = format_style == 'pretty-json'
        if pretty_json:
            format_style = 'json'
        FMTR[format_style]

        urlconf = opt_urlconf

        views = []
        if not hasattr(settings, urlconf):
            raise CommandError(
                f'Settings module {settings} does not have the attribute {urlconf}.'
            )

        try:
            urlconf = __import__(getattr(settings, urlconf), {}, {}, [''])
        except Exception as e:
            if options['traceback']:
                import traceback

                traceback.print_exc()
            raise CommandError(
                f'Error occurred while trying to load {getattr(settings, urlconf)}: {e!s}'
            )

        view_functions = self.extract_views_from_urlpatterns(
            urlconf.urlpatterns
        )
        for func, regex, url_name in view_functions:
            if hasattr(func, '__globals__'):
                func_globals = func.__globals__
            elif hasattr(func, 'func_globals'):
                func_globals = func.func_globals
            else:
                func_globals = {}

            decorators = [d for d in decorator if d in func_globals]

            if isinstance(func, functools.partial):
                func = func.func
                decorators.insert(0, 'functools.partial')

            if hasattr(func, 'view_class'):
                func = func.view_class
            if hasattr(func, '__name__'):
                func_name = func.__name__
            elif hasattr(func, '__class__'):
                func_name = f'{func.__class__.__name__}()'
            else:
                func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))

            module = f'{func.__module__}.{func_name}'
            url_name = url_name or ''
            url = simplify_regex(regex)
            decorator = ', '.join(decorators)

            views.append({
                'url': str(url),
                'module': str(module),
                'name': str(url_name),
            })
        if options.get('search'):
            views = [
                d
                for d in views
                if all(
                    word in d['module'] or word in d['url'] or word in d['name']
                    for word in options.get('search').split(' ')
                )
            ]
        views = sorted(views, key=operator.itemgetter('url'))
        # if not opt_unsorted and format_style != 'json':

        # if format_style == 'aligned':
        #    views = [row.split(',', 3) for row in views]
        #    widths = [len(max(columns, key=len)) for columns in zip(*views)]
        #    views = [
        #        '   '.join('{0:<{1}}'.format(cdata, width) for width, cdata in zip(widths, row))
        #        for row in views
        #    ]
        # elif format_style == 'table':
        #    # Reformat all data and show in a table format

        #    views = [row.split(',', 3) for row in views]
        #    widths = [len(max(columns, key=len)) for columns in zip(*views)]
        #    table_views = []

        #    header = (style.MODULE_NAME('URL'), style.MODULE_NAME('Module'), style.MODULE_NAME('Name'), style.MODULE_NAME('Decorator'))
        #    table_views.append(
        #        ' | '.join('{0:<{1}}'.format(title, width) for width, title in zip(widths, header))
        #    )
        #    table_views.append('-+-'.join('-' * width for width in widths))

        #    for row in views:
        #        table_views.append(
        #            ' | '.join('{0:<{1}}'.format(cdata, width) for width, cdata in zip(widths, row))
        #        )

        #    # Replace original views so we can return the same object
        #    views = table_views

        # elif format_style == 'json':
        #    if pretty_json:
        #        return json.dumps(views, indent=4)
        #    return json.dumps(views)

        return list(views)

    def extract_views_from_urlpatterns(
        self, urlpatterns, base='', namespace=None
    ):
        """
        Return a list of views from a list of urlpatterns.

        Each object in the returned list is a three-tuple: (view_func, regex, name)
        """
        views = []
        for p in urlpatterns:
            if isinstance(p, URLPattern | RegexURLPattern):
                try:
                    if not p.name:
                        name = p.name
                    elif namespace:
                        name = f'{namespace}:{p.name}'
                    else:
                        name = p.name
                    pattern = describe_pattern(p)
                    views.append((p.callback, base + pattern, name))
                except ViewDoesNotExist:
                    continue
            elif isinstance(p, URLResolver | RegexURLResolver):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                if namespace and p.namespace:
                    namespace_ = f'{namespace}:{p.namespace}'
                else:
                    namespace_ = p.namespace or namespace
                pattern = describe_pattern(p)
                if isinstance(p, LocaleRegexURLResolver):
                    for language in self.LANGUAGES:
                        with translation.override(language[0]):
                            views.extend(
                                self.extract_views_from_urlpatterns(
                                    patterns,
                                    base + pattern,
                                    namespace=namespace_,
                                )
                            )
                else:
                    views.extend(
                        self.extract_views_from_urlpatterns(
                            patterns, base + pattern, namespace=namespace_
                        )
                    )
            elif hasattr(p, '_get_callback'):
                try:
                    views.append((
                        p._get_callback(),
                        base + describe_pattern(p),
                        p.name,
                    ))
                except ViewDoesNotExist:
                    continue
            elif hasattr(p, 'url_patterns') or hasattr(p, '_get_url_patterns'):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(
                    self.extract_views_from_urlpatterns(
                        patterns,
                        base + describe_pattern(p),
                        namespace=namespace,
                    )
                )
            else:
                raise TypeError(
                    f'{p} does not appear to be a urlpattern object'
                )
        return views
