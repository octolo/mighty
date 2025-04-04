from django.utils.translation import gettext_lazy as _

v_log = _('log')
vp_log = _('logs')

args = _(
    'The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when there is only one argument, and it is a dictionary).'
)
asctime = _(
    "Human-readable time when the LogRecord was created. By default this is of the form '2003-07-08 16:49:45,896' (the numbers after the comma are millisecond portion of the time)."
)
created = _('Time when the LogRecord was created (as returned by time.time()).')
exc_info = _(
    'Exception tuple (à la sys.exc_info) or, if no exception has occurred, None.'
)
filename = _('Filename portion of pathname.')
funcName = _('Name of function containing the logging call.')
levelname = _(
    "Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')."
)
levelno = _(
    'Numeric logging level for the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).'
)
lineno = _(
    'Source line number where the logging call was issued (if available).'
)
message = _(
    'The logged message, computed as msg % args. This is set when Formatter.format() is invoked.'
)
module = _('Module (name portion of filename).')
msecs = _('Millisecond portion of the time when the LogRecord was created.')
msg = _(
    "The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Utilisation d'objets arbitraires comme messages)."
)
name = _('Name of the logger used to log the call.')
pathname = _(
    'Full pathname of the source file where the logging call was issued (if available).'
)
process = _('Process ID (if available).')
processName = _('Process name (if available).')
relativeCreated = _(
    'Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.'
)
stack_info = _(
    'Stack frame information (where available) from the bottom of the stack in the current thread, up to and including the stack frame of the logging call which resulted in the creation of this record.'
)
thread = _('Thread ID (if available).')
threadNa = _('Thread name (if available).')

v_changelog = _('change log')
vp_changelog = _('changes logs')
