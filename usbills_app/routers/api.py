"""API router module for direct data access."""

# standard library imports
from datetime import date
from typing import Optional

# third party imports
from fastapi import APIRouter, Query, HTTPException, status, Path

# app imports
from usbills_app.db import managed_async_session
from usbills_app.db.query import BillQuery, StatsQuery
from usbills_app.logger import create_logger
from usbills_app.routers.models import (
    BillListSlim,
    BillSlim,
    BillFull,
    BillSection,
    BillAggregateStats,
)

# create router
router = APIRouter()

# get logger
LOGGER = create_logger(__name__)


def get_slim_bills(bills: list[dict]) -> list[dict]:
    # get the list and remove the text, markdown, and html fields
    for bill in bills:
        bill.pop("text", None)
        bill.pop("markdown", None)
        bill.pop("html", None)
        bill["api_url"] = f"/api/bills/{bill['slug']}"

    return bills


@router.get("/api/bills", response_model=BillListSlim, tags=["api"])
async def api_list_bills(
    limit: Optional[int] = Query(
        10, alias="limit", description="Maximum number of bills to return", gt=0, lt=100
    ),
    offset: Optional[int] = Query(
        0, alias="offset", description="Number of bills to skip for pagination", gte=0
    ),
    start_date: Optional[date] = Query(
        None, alias="start_date", description="Start date for filtering bills"
    ),
    end_date: Optional[date] = Query(
        None, alias="end_date", description="End date for filtering bills"
    ),
) -> BillListSlim:
    """Get list of bills with pagination and date filtering.

    Args:
        limit: Maximum number of bills to return
        offset: Number of bills to skip for pagination
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        BillListSlim: List of bills with pagination and date filtering.
    """
    async with managed_async_session() as session:
        bill_query = BillQuery(session)

        if start_date:
            bills = await bill_query.get_by_date(
                start_date, end_date, limit=limit, offset=offset
            )
        else:
            bills = await bill_query.get_newest_bills(limit=limit, offset=offset)

        # convert to slim dicts
        slim_bills = [
            BillSlim.model_validate(bill)
            for bill in get_slim_bills([bill.to_dict() for bill in bills])
        ]

        # convert to pydantic response
        return BillListSlim(total=len(slim_bills), bills=slim_bills)


@router.get("/api/bills/{slug}", response_model=BillFull, tags=["api"])
async def api_get_bill_details(
    slug: str = Path(..., alias="slug", description="Bill slug or package_id"),
) -> BillFull:
    """Get bill details by slug or package_id, which includes the full text
    and section-level details of a bill.

    Args:
        slug: Bill slug or package_id

    Returns:
        BillFull: Bill details including sections and other metadata.
    """
    async with managed_async_session() as session:
        bill_query = BillQuery(session)

        # Try to get bill by slug
        bill = await bill_query.get_by_slug(slug)
        if not bill:
            # Try to get by package id
            bill = await bill_query.get_by_package_id(slug)

        if not bill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bill with slug/package_id {slug} not found",
            )

        # Get bill data
        bill_data = bill.to_dict()

        sections = [
            BillSection.model_validate(section.to_dict())
            for section in await bill_query.get_bill_sections(bill)
        ]
        bill_data["sections"] = sections

        return BillFull.model_validate(bill_data)


@router.get("/api/search", response_model=BillListSlim, tags=["api", "search"])
async def api_search_bills(
    q: str = Query("", alias="q", description="Search query"),
) -> BillListSlim:
    """Search for bills using a query string, which is processed by a Solr backend
    that includes the text and metadata fields of all bills.

    Args:
        q: Search query string

    Returns:
        BillListSlim: List of bills matching the search query.
    """
    from usbills_app.utils.solr import SolrClient

    try:
        solr = SolrClient()
        search_results = solr.search("fbs", q)

        async with managed_async_session() as session:
            bill_query = BillQuery(session)
            bills = []

            for doc in search_results["response"]["docs"]:
                bill = await bill_query.get_by_package_id(doc["package_id"])
                if bill:
                    bills.append(bill.to_dict())

            # convert to slim dicts
            slim_bills = [
                BillSlim.model_validate(bill) for bill in get_slim_bills(bills)
            ]

            return BillListSlim(total=len(slim_bills), bills=slim_bills)
    except Exception as e:
        LOGGER.error(f"Error searching bills: {str(e)}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error searching bills",
    )


@router.get("/api/stats", response_model=BillAggregateStats, tags=["api"])
async def api_get_bill_stats() -> BillAggregateStats:
    """Get aggregate bill statistics from the database.

    Returns:
        BillAggregateStats: Aggregate statistics about bills.
    """
    async with managed_async_session() as session:
        stats_query = StatsQuery(session)

        # Get counts
        total_bills = await stats_query.get_total_bills()
        total_sections = await stats_query.get_total_sections()
        total_tokens = await stats_query.get_total_tokens()
        total_sentences = await stats_query.get_total_sentences()

        # Get distributions by type/chamber/version
        bills_by_type = await stats_query.get_bills_by_type()
        bills_by_chamber = await stats_query.get_bills_by_chamber()
        bills_by_version = await stats_query.get_bills_by_version()

        # Get token stats
        token_stats = await stats_query.get_token_stats()
        section_stats = await stats_query.get_section_stats()
        entropy_stats = await stats_query.get_entropy_stats()

        return BillAggregateStats.model_validate(
            {
                "total_bills": total_bills,
                "total_sections": total_sections,
                "total_tokens": total_tokens,
                "total_sentences": total_sentences,
                "bills_by_type": bills_by_type,
                "bills_by_chamber": bills_by_chamber,
                "bills_by_version": bills_by_version,
                "token_stats": token_stats,
                "section_stats": section_stats,
                "entropy_stats": entropy_stats,
            }
        )
