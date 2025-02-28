from django.utils.translation import gettext_lazy as _

STRICTLY = 'STRICTLY'
PERFORMANCE = 'PERFORMANCE'
FUNCTIONAL = 'FUNCTIONAL'
TARGETING = 'TARGETING'
SOCIAL = 'SOCIAL'

STRICTLY_LABEL = _('Strictly Necessary Cookies.')
PERFORMANCE_LABEL = _('Performance Cookies.')
FUNCTIONAL_LABEL = _('Functional Cookies.')
TARGETING_LABEL = _('Targeting Cookies.')
SOCIAL_LABEL = _('Social Media Cookies.')

STRICTLY_DESC = _(
    'These cookies are necessary for the website to function and cannot be switched off in our systems. They are usually only set in response to actions made by you which amount to a request for services, such as setting your privacy preferences, logging in or filling in forms. You can set your browser to block or alert you about these cookies, but some parts of the site will not then work. These cookies do not store any personally identifiable information.'
)
PERFORMANCE_DESC = _(
    'These cookies allow us to count visits and traffic sources so we can measure and improve the performance of our site. They help us to know which pages are the most and least popular and see how visitors move around the site. All information these cookies collect is aggregated and therefore anonymous. If you do not allow these cookies we will not know when you have visited our site, and will not be able to monitor its performance.'
)
FUNCTIONAL_DESC = _(
    'These cookies enable the website to provide enhanced functionality and personalisation. They may be set by us or by third party providers whose services we have added to our pages. If you do not allow these cookies then some or all of these services may not function properly.'
)
TARGETING_DESC = _(
    'These cookies may be set through our site by our advertising partners. They may be used by those companies to build a profile of your interests and show you relevant adverts on other sites. They do not store directly personal information, but are based on uniquely identifying your browser and internet device. If you do not allow these cookies, you will experience less targeted advertising.'
)
SOCIAL_DESC = _(
    'These cookies are set by a range of social media services that we have added to the site to enable you to share our content with your friends and networks. They are capable of tracking your browser across other sites and building up a profile of your interests. This may impact the content and messages you see on other websites you visit. If you do not allow these cookies you may not be able to use or see these sharing tools.'
)

CATEGORY = (
    (STRICTLY, STRICTLY_LABEL),
    (PERFORMANCE, PERFORMANCE_LABEL),
    (FUNCTIONAL, FUNCTIONAL_LABEL),
    (TARGETING, TARGETING_LABEL),
    (SOCIAL, SOCIAL_LABEL),
)
