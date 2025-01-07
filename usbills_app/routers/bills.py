"""
Routes related to bills and bill sections.
"""

# packages
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
import markdown

# project
from usbills_app.db import managed_async_session
from usbills_app.db.query import BillQuery, StatsQuery
from usbills_app.templates import get_template_renderer
from usbills_app.utils.templates import prepare_bill_for_template
from usbills_app.logger import create_logger

# create router
router = APIRouter()

# get template renderer
template_renderer = get_template_renderer()

# get logger
LOGGER = create_logger(__name__)


# backwards-compat route at /{slug}.html
@router.get("/{slug}.html", response_class=HTMLResponse, tags=["bill", "legacy"])
async def bill_details_legacy(slug: str) -> str:
    """Bill details route handler for details on bills and bill sections.

    Args:
        slug (str): Bill slug identifier

    Returns:
        str: Rendered bill_details template with bill details
    """
    LOGGER.info(f"Redirecting to /bills/{slug}")
    return f'<meta http-equiv="refresh" content="0; URL=/bills/{slug}">'


# backwards-compat route at /{slug}.json
@router.get("/{slug}.json", response_class=HTMLResponse, tags=["bill", "legacy"])
async def bill_json_legacy(slug: str) -> str:
    """Return bill JSON data.

    Args:
        slug (str): Bill slug identifier

    Returns:
        dict: Bill data as JSON
    """
    LOGGER.info(f"Redirecting to /bills/{slug}/json")
    return f'<meta http-equiv="refresh" content="0; URL=/bills/{slug}/json">'


# backwards-compat route at /{slug}.pdf to redirect to /bills/{slug}
@router.get("/{slug}.pdf", response_class=HTMLResponse, tags=["bill", "legacy"])
async def bill_pdf_legacy(slug: str) -> str:
    """Redirect to bill details route.

    Args:
        slug (str): Bill slug identifier

    Returns:
        str: Redirect to bill details route
    """
    LOGGER.info(f"Redirecting to /bills/{slug}")
    return f'<meta http-equiv="refresh" content="0; URL=/bills/{slug}">'


@router.get("/bills/{slug}", response_class=HTMLResponse, tags=["bill", "html"])
async def bill_details(slug: str) -> str:
    """Bill details route handler for details on bills and bill sections.

    Args:
        slug (str): Bill slug identifier

    Returns:
        str: Rendered bill_details template with bill details
    """
    async with managed_async_session() as session:
        # try to get bill by slug
        bill_query = BillQuery(session)
        bill = await bill_query.get_by_slug(slug)
        if not bill:
            # try to get by package id
            bill = await bill_query.get_by_package_id(slug)
        if not bill:
            return f"Bill not found: {slug}"

        # get sections
        sections = [
            section.to_dict() for section in await bill_query.get_bill_sections(bill)
        ]
        for section in sections:
            # convert markdown to HTML
            section["summary"] = markdown.markdown(section["summary"])

        # get statistics
        stats_query = StatsQuery(session)
        token_quantile = await stats_query.get_token_quantile(bill.num_tokens)
        section_quantile = await stats_query.get_section_quantile(bill.num_sections)
        sentence_quantile = await stats_query.get_sentence_quantile(bill.num_sentences)
        bills_by_type = await stats_query.get_bills_by_type()
        bills_by_chamber = await stats_query.get_bills_by_chamber()

        # set up bill with computed fields
        bill = prepare_bill_for_template(bill)

        # build context with bill details and stats
        context = {
            "bill": bill,
            "sections": sections,
            "bills_by_type": bills_by_type,
            "bills_by_chamber": bills_by_chamber,
            "token_percentile": token_quantile,
            "section_percentile": section_quantile,
            "sentence_percentile": sentence_quantile,
            "title": f"{bill['legis_num']} - {bill['title']}",
            "description": f"{bill['eli5']}",
        }
        return await template_renderer.render("bill.html", context)


@router.get("/bills/{slug}/json", response_class=JSONResponse, tags=["bill"])
async def bill_json(slug: str) -> dict:
    """Return bill JSON data.

    Args:
        slug (str): Bill slug identifier

    Returns:
        dict: Bill data as JSON
    """
    async with managed_async_session() as session:
        # try to get bill by slug
        bill_query = BillQuery(session)
        bill = await bill_query.get_by_slug(slug)
        if not bill:
            # try to get by package id
            bill = await bill_query.get_by_package_id(slug)
        if not bill:
            return {"error": f"Bill not found: {slug}"}

        # get sections
        sections = [
            section.to_dict() for section in await bill_query.get_bill_sections(bill)
        ]

        # prepare bill data
        bill_data = prepare_bill_for_template(bill)
        bill_data["sections"] = sections

        return bill_data
