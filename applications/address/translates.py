from django.utils.translation import gettext_lazy as _

v_address = _('Address')
vp_address = _('Addresses')

WAYS = (
    ('ALL', _('Allée')),
    ('AV', _('Avenue')),
    ('BD', _('Boulevard')),
    ('CAR', _('Carrefour')),
    ('CHE', _('Chemin')),
    ('CHS', _('Chaussée')),
    ('CITE', _('Cité')),
    ('COR', _('Corniche')),
    ('CRS', _('Cours')),
    ('DOM', _('Domaine')),
    ('DSC', _('Descente')),
    ('ECA', _('Ecart')),
    ('ESP', _('Esplanade')),
    ('FG', _('Faubourg')),
    ('GR', _('Grande Rue')),
    ('HAM', _('Hameau')),
    ('HLE', _('Halle')),
    ('IMP', _('Impasse')),
    ('LD', _('Lieu-dit')),
    ('LOT', _('Lotissement')),
    ('MAR', _('Marché')),
    ('MTE', _('Montée')),
    ('PAS', _('Passage')),
    ('PL', _('Place')),
    ('PLN', _('Plaine')),
    ('PLT', _('Plateau')),
    ('PRO', _('Promenade')),
    ('PRV', _('Parvis')),
    ('QUA', _('Quartier')),
    ('QUAI', _('Quai')),
    ('RES', _('Résidence')),
    ('RLE', _('Ruelle')),
    ('ROC', _('Rocade')),
    ('RPT', _('Rond-point')),
    ('RTE', _('Route')),
    ('RUE', _('Rue')),
    ('SEN', _('Sente - Sentier')),
    ('SQ', _('Square')),
    ('TPL', _('Terre-plein')),
    ('TRA', _('Traverse')),
    ('VLA', _('Villa')),
    ('VLGE', _('Village')),
)

address = _('address')
complement = _('complement')
locality = _('locality')
postal_code = _('postal code')
state = _('state')
state_code = _('state code')
country = _('country')
country_code = _('country code')
cedex = _('cedex')
cedex_code = _('cedex code')

validate_postal_state_code = '"%s" or "%s" must be filled' % (postal_code, state_code)