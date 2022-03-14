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

address = _('Adresse/Address')
complement = _('Complément/Complement')
locality = _('Ville/City')
postal_code = _('Code postal/Postal code')
state = _('Etat/State')
state_code = _("Code de de l'état/State code")
country = _('Pays/Country')
country_code = _('Code du pays (Fr)/Country code (US)')
cedex = _('Cedex')
cedex_code = _('Code cedex/Cedex code')
special = _('Informations spéciales/Special information')
index = _('Indice/Index')

validate_postal_state_code = '"%s" or "%s" must be filled' % (postal_code, state_code)