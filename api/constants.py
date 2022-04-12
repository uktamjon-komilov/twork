from django.utils.translation import gettext as _

INDIVIDUAL = "individual"
LEGAL_ENTITY = "legal_entity"

WORKER_TYPE = [
    ("all", _("All")),
    ("freelancer", _("Freelancer")),
    ("team", _("Team")),
    ("company", _("Company"))
]