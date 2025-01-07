"""
Routes related to the index/root of the application.
"""

# imports
from datetime import date
from typing import Optional

# packages
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

# project
from usbills_app.db import managed_async_session
from usbills_app.db.models.constants import BILL_TYPE_CODES, BILL_VERSION_CODES
from usbills_app.db.query import BillQuery, StatsQuery
from usbills_app.templates import get_template_renderer
from usbills_app.utils.templates import prepare_bill_for_template

# create router
router = APIRouter()

# get template renderer
template_renderer = get_template_renderer()

# bills per page
BILLS_PER_PAGE = 5


@router.get("/", response_class=HTMLResponse, tags=["html"])
async def index(
    limit: int = Query(
        BILLS_PER_PAGE,
        alias="limit",
        ge=1,
        le=100,
        description="Number of bills per page",
    ),
    offset: int = Query(0, alias="offset", ge=0, description="Offset for pagination"),
    page: int = Query(1, alias="page", ge=1, description="Page number for pagination"),
    start_date: Optional[date] = Query(
        None, alias="start_date", description="Start date filter"
    ),
    end_date: Optional[date] = Query(
        None, alias="end_date", description="End date filter"
    ),
) -> str:
    """Base route handler that returns the most recent bills with stats and pagination.

    Args:
        limit (int): Number of bills per page
        offset (int): Offset for pagination
        page (int): Page number for pagination
        start_date (Optional[date]): Optional start date filter
        end_date (Optional[date]): Optional end date filter

    Returns:
        str: Rendered index template with recent bills, statistics and pagination
    """
    async with managed_async_session() as session:
        # calculate offset from page if provided
        if page > 1:
            offset = (page - 1) * limit

        # get bills
        bill_query = BillQuery(session)
        if start_date:
            bills = await bill_query.get_by_date(
                start_date, end_date, limit=limit, offset=offset
            )
        else:
            bills = await bill_query.get_newest_bills(limit=limit, offset=offset)
        bills = [prepare_bill_for_template(bill) for bill in bills]

        # get one more bill to check if there are more pages
        if start_date:
            next_bills = await bill_query.get_by_date(
                start_date, end_date, limit=1, offset=offset + limit
            )
        else:
            next_bills = await bill_query.get_newest_bills(
                limit=1, offset=offset + limit
            )
        has_more_bills = len(next_bills) > 0

        # get stats
        stats_query = StatsQuery(session)
        total_bills = await stats_query.get_total_bills()
        total_tokens = await stats_query.get_total_tokens()
        total_sections = await stats_query.get_total_sections()
        bills_by_type = await stats_query.get_bills_by_type()
        bills_by_chamber = await stats_query.get_bills_by_chamber()

        # render template with bills, stats and pagination info
        context = {
            "bills": bills,
            "total_bills": total_bills,
            "total_tokens": total_tokens,
            "total_sections": total_sections,
            "bills_by_type": bills_by_type,
            "bills_by_chamber": bills_by_chamber,
            "page": page,
            "limit": limit,
            "offset": offset,
            "has_more_bills": has_more_bills,
            "start_date": start_date,
            "end_date": end_date,
            "title": "Recent Bills",
            "description": "Recent bills from the US Congress with analysis and statistics",
        }
        return await template_renderer.render("index.html", context)


@router.get("/leaderboard", response_class=HTMLResponse, tags=["html"])
async def leaderboard(limit: int = 20) -> str:
    """Get leaderboard of bills by size.

    Args:
        limit (int): Number of bills to return

    Returns:
        str: Rendered leaderboard template
    """
    async with managed_async_session() as session:
        # get top 100 bills by tokens
        bill_query = BillQuery(session)
        big_bills = await bill_query.get_largest_bills(limit=limit)
        big_bills = [prepare_bill_for_template(bill) for bill in big_bills]

        stats_query = StatsQuery(session)
        total_bills = await stats_query.get_total_bills()

        # template context
        context = {
            "bills": big_bills,
            "total_bills": total_bills,
            "title": "Largest Bills Leaderboard",
            "description": "Largest bills in Congress by number of words",
        }

        return await template_renderer.render("leaderboard.html", context)


@router.get("/stats", response_class=HTMLResponse, tags=["html"])
async def stats() -> str:
    """Statistics page handler that returns aggregate bill statistics.

    Returns:
        str: Rendered stats template with bill statistics
    """
    async with managed_async_session() as session:
        # Get bill statistics
        stats_query = StatsQuery(session)

        # get bills by type first, then map keys to descriptions
        bills_by_type = await stats_query.get_bills_by_type()
        bills_by_type = {
            BILL_TYPE_CODES.get(k.lower(), k): v for k, v in bills_by_type.items()
        }

        # get bills by version first, then map keys to descriptions
        bills_by_version = await stats_query.get_bills_by_version()
        bills_by_version = {
            BILL_VERSION_CODES.get(k.lower(), k): v for k, v in bills_by_version.items()
        }

        # bills by chamber
        bills_by_chamber = await stats_query.get_bills_by_chamber()

        # sort the groups by count descending
        bills_by_type = dict(
            sorted(bills_by_type.items(), key=lambda item: item[1], reverse=True)
        )
        bills_by_chamber = dict(
            sorted(bills_by_chamber.items(), key=lambda item: item[1], reverse=True)
        )
        bills_by_version = dict(
            sorted(bills_by_version.items(), key=lambda item: item[1], reverse=True)
        )

        # Build stats dictionary
        bill_stats = {
            # Get count totals
            "total_bills": await stats_query.get_total_bills(),
            "total_sections": await stats_query.get_total_sections(),
            "total_tokens": await stats_query.get_total_tokens(),
            "total_sentences": await stats_query.get_total_sentences(),
            # Get bills by type/chamber
            "bills_by_type": bills_by_type,
            "bills_by_version": bills_by_version,
            "bills_by_chamber": bills_by_chamber,
        }

        # Get token stats
        token_stats = await stats_query.get_token_stats()
        bill_stats.update(
            {
                "min_tokens": token_stats["min"],
                "max_tokens": token_stats["max"],
                "mean_tokens": token_stats["mean"],
                "p25_tokens": token_stats["p25"],
                "p50_tokens": token_stats["p50"],
                "p75_tokens": token_stats["p75"],
            }
        )

        # Get section stats
        section_stats = await stats_query.get_section_stats()
        bill_stats.update(
            {
                "min_sections": section_stats["min"],
                "max_sections": section_stats["max"],
                "mean_sections": section_stats["mean"],
                "p25_sections": section_stats["p25"],
                "p50_sections": section_stats["p50"],
                "p75_sections": section_stats["p75"],
            }
        )

        # Get entropy
        entropy_stats = await stats_query.get_entropy_stats()
        bill_stats.update(
            {
                "min_entropy": entropy_stats["min"],
                "max_entropy": entropy_stats["max"],
                "mean_entropy": entropy_stats["mean"],
                "p25_entropy": entropy_stats["p25"],
                "p50_entropy": entropy_stats["p50"],
                "p75_entropy": entropy_stats["p75"],
            }
        )

        # Render template with all stats
        return await template_renderer.render("stats.html", {"stats": bill_stats})


@router.get("/privacy", response_class=HTMLResponse, tags=["html"])
async def privacy() -> str:
    """Privacy route handler that returns the privacy policy page.

    Returns:
        str: Rendered privacy template
    """
    context = {
        "title": "Privacy Policy",
        "description": "Privacy policy for the US Bills Analysis web app",
    }
    return await template_renderer.render("privacy.html", context)


@router.get("/about", response_class=HTMLResponse, tags=["html"])
async def about() -> str:
    """About route handler that returns the about page.

    Returns:
        str: Rendered about template
    """
    context = {
        "title": "About",
        "description": "About the US Bills Analysis web app",
    }
    return await template_renderer.render("about.html", context)
