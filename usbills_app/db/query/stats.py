"""
Query and calculation patterns related to aggregate statistics for bills.
"""

# imports
from dataclasses import dataclass
from typing import Optional, Dict

# packages
from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession

# project
from usbills_app.db.models import Bill, BillSection
from usbills_app.db.query.bills import BillQuery
from usbills_app.logger import create_logger

# create logger
LOGGER = create_logger(__name__)


@dataclass
class BillStats:
    """Container for bill statistics.

    Contains both population statistics about bill counts, tokens, etc.
    and relative statistics for individual bills.
    """

    # Population counts
    total_bills: int
    total_sections: int
    total_tokens: int
    total_sentences: int

    # Token stats
    min_tokens: float
    max_tokens: float
    mean_tokens: float
    median_tokens: float
    p25_tokens: float
    p75_tokens: float

    # Section stats
    min_sections: float
    max_sections: float
    mean_sections: float
    median_sections: float
    p25_sections: float
    p75_sections: float

    # Sentence stats
    min_sentences: float
    max_sentences: float
    mean_sentences: float
    median_sentences: float
    p25_sentences: float
    p75_sentences: float

    # Population counts by type
    bills_by_type: Dict[str, int]
    bills_by_chamber: Dict[str, int]
    bills_by_version: Dict[str, int]

    # Stats for specific bill (optional)
    bill_token_quantile: Optional[float] = None
    bill_section_quantile: Optional[float] = None
    bill_sentence_quantile: Optional[float] = None


class StatsQuery:
    """Class for calculating bill statistics."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
        self.bill_query = BillQuery(session)

    async def get_total_bills(self) -> int:
        """Get total number of bills.

        Returns:
            int: Total number of bills
        """
        stmt = select(func.count()).select_from(Bill)
        return await self.session.scalar(stmt)

    async def get_total_sections(self) -> int:
        """Get total number of bill sections.

        Returns:
            int: Total number of bill sections
        """
        stmt = select(func.count()).select_from(BillSection)
        return await self.session.scalar(stmt)

    async def get_total_tokens(self) -> int:
        """Get total number of tokens across all bills.

        Returns:
            int: Total number of tokens
        """
        stmt = select(func.sum(Bill.num_tokens)).select_from(Bill)
        return await self.session.scalar(stmt)

    async def get_total_sentences(self) -> int:
        """Get total number of sentences across all bills.

        Returns:
            int: Total number of sentences
        """
        stmt = select(func.sum(Bill.num_sentences)).select_from(Bill)
        return await self.session.scalar(stmt)

    async def get_token_stats(self) -> Dict[str, float]:
        """Get token statistics across all bills.

        Returns:
            Dict with min, max, mean, p25, p50, p75 token counts
        """
        return await self._calculate_percentiles(Bill.num_tokens)

    async def get_section_stats(self) -> Dict[str, float]:
        """Get section statistics across all bills.

        Returns:
            Dict with min, max, mean, p25, p50, p75 section counts
        """
        return await self._calculate_percentiles(Bill.num_sections)

    async def get_sentence_stats(self) -> Dict[str, float]:
        """Get sentence statistics across all bills.

        Returns:
            Dict with min, max, mean, p25, p50, p75 sentence counts
        """
        return await self._calculate_percentiles(Bill.num_sentences)

    async def get_entropy_stats(self) -> Dict[str, float]:
        """Get entropy statistics across all bills.

        Returns:
            Dict with min, max, mean, p25, p50, p75 entropy counts
        """
        return await self._calculate_percentiles(Bill.token_entropy)

    async def get_bills_by_type(self) -> Dict[str, int]:
        """Get count of bills by type.

        Returns:
            Dict mapping bill types to counts
        """
        return await self._count_by_field(Bill.bill_type)

    async def get_bills_by_chamber(self) -> Dict[str, int]:
        """Get count of bills by chamber.

        Returns:
            Dict mapping chambers to bill counts
        """
        return await self._count_by_field(Bill.current_chamber)

    async def get_bills_by_version(self) -> Dict[str, int]:
        """Get count of bills by version.

        Returns:
            Dict mapping bill versions to counts
        """
        return await self._count_by_field(Bill.bill_version)

    async def get_token_quantile(self, value: float) -> float:
        """Get percentile rank of a token count.

        Args:
            value: Token count to get percentile for

        Returns:
            Percentile rank (0-1)
        """
        return await self._calculate_quantile(Bill.num_tokens, value)

    async def get_section_quantile(self, value: float) -> float:
        """Get percentile rank of a section count.

        Args:
            value: Section count to get percentile for

        Returns:
            Percentile rank (0-1)
        """
        return await self._calculate_quantile(Bill.num_sections, value)

    async def get_sentence_quantile(self, value: float) -> float:
        """Get percentile rank of a sentence count.

        Args:
            value: Sentence count to get percentile for

        Returns:
            Percentile rank (0-1)
        """
        return await self._calculate_quantile(Bill.num_sentences, value)

    async def get_entropy_quantile(self, value: float) -> float:
        """Get percentile rank of a token entropy.

        Args:
            value: Token entropy to get percentile for

        Returns:
            Percentile rank (0-1)
        """
        return await self._calculate_quantile(Bill.token_entropy, value)

    async def _calculate_percentiles(self, column) -> Dict[str, float]:
        """Calculate statistical measures for a numeric column.

        Args:
            column: SQLAlchemy column to analyze

        Returns:
            Dict containing min, max, mean, p25, p50 (median), p75
        """
        stmt = select(
            func.min(column).label("min"),
            func.max(column).label("max"),
            func.avg(column).label("mean"),
            func.percentile_cont(0.25).within_group(column).label("p25"),
            func.percentile_cont(0.5).within_group(column).label("p50"),
            func.percentile_cont(0.75).within_group(column).label("p75"),
        )

        result = await self.session.execute(stmt)
        row = result.fetchone()

        return {
            "min": row.min,
            "max": row.max,
            "mean": row.mean,
            "p25": row.p25,
            "p50": row.p50,
            "p75": row.p75,
        }

    async def _calculate_quantile(self, column, value: float) -> float:
        """Calculate percentile rank of a value for a column.

        Args:
            column: SQLAlchemy column to analyze
            value: Value to calculate percentile for

        Returns:
            float: Percentile rank (0-1)
        """
        stmt = select(
            func.count().filter(column < value).cast(Integer)
            * 100.0
            / func.count().over()
        )

        return await self.session.scalar(stmt)

    async def _count_by_field(self, field) -> Dict[str, int]:
        """Count number of bills for each distinct value in a field.

        Args:
            field: SQLAlchemy column to group by

        Returns:
            Dict mapping field values to counts
        """
        stmt = select(field, func.count().label("count")).group_by(field)

        result = await self.session.execute(stmt)
        return {row[0]: row[1] for row in result}
