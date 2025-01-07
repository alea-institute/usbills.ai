"""
Routes related to search functionality.
"""

# packages
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

# project
from usbills_app.db import managed_async_session
from usbills_app.db.query import BillQuery
from usbills_app.templates import get_template_renderer
from usbills_app.utils.solr import SolrClient
from usbills_app.utils.templates import prepare_bill_for_template
from usbills_app.logger import create_logger

# create router
router = APIRouter()

# get template renderer
template_renderer = get_template_renderer()

# get logger
LOGGER = create_logger(__name__)


@router.get("/search", response_class=HTMLResponse, tags=["html", "search"])
async def search(q: str = "") -> str:
    """Search bills using Solr and render results.

    Args:
        q: Search query string

    Returns:
        str: Rendered template with search results
    """
    LOGGER.info(f"Searching bills with query: {q}")

    # Initialize solr client
    solr = SolrClient()

    try:
        # Search solr
        search_results = solr.search("fbs", q)
        LOGGER.debug(f"Got {len(search_results['response']['docs'])} results from Solr")

        # Get bills from database
        async with managed_async_session() as session:
            bill_query = BillQuery(session)
            bills = []

            for doc in search_results["response"]["docs"]:
                bill = await bill_query.get_by_package_id(doc["package_id"])
                if bill:
                    bills.append(prepare_bill_for_template(bill))

            LOGGER.debug(f"Retrieved {len(bills)} bills from database")

            # Build template context
            context = {
                "bills": bills,
                "page": 1,
                "limit": len(bills),
                "offset": 0,
                "total_bills": search_results["response"]["numFound"],
                "has_more_bills": False,
                "title": f"Search Results for {q}",
                "description": f"Search results for bills matching '{q}'",
                "q": q,
            }

            return await template_renderer.render("index.html", context)

    except Exception as e:
        LOGGER.error(f"Error searching bills: {str(e)}")
        return f"Error searching bills: {str(e)}"

    finally:
        solr.close()
