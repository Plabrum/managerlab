from app.actions.enums import ActionGroupType
from app.actions.registry import action_group_factory
from app.payments.models import Invoice


invoice_actions = action_group_factory(
    ActionGroupType.InvoiceActions, model_type=Invoice
)
