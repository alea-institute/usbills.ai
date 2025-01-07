"""
jinja2 template utils
"""

# imports
from typing import Dict

# packages
import markdown

# project
from usbills_app.db.models import BILL_VERSION_CODES
from usbills_app.utils.slugs import get_default_slug
from usbills_app.db.models import Bill


def prepare_bill_for_template(bill: Bill) -> Dict:
    """
    Prepare a bill object for rendering in a template.

    Args:
        bill (Bill): Bill object

    Returns:
        Dict: Prepared bill object properly formatted for jinja2 rendering
    """
    # detach the bill object from the session
    bill_dict = bill.to_dict()

    # Add some computed fields used in the template
    bill_dict["slug"] = get_default_slug(bill.legis_num, bill.title, bill.bill_version)
    bill_dict["bill_version_description"] = BILL_VERSION_CODES.get(
        bill.bill_version.lower(), "Unknown"
    )
    bill_dict["summary"] = markdown.markdown(bill.summary)
    bill_dict["html_description"] = str(bill.eli5)
    bill_dict["eli5"] = markdown.markdown(bill.eli5)
    bill_dict["commentary"] = markdown.markdown(bill.commentary)
    bill_dict["money_commentary"] = (
        markdown.markdown(bill.money_commentary) if bill.money_commentary else None
    )

    return bill_dict
