"""
Basic query patterns for bills.
"""

# imports
import datetime
from typing import Sequence, Optional

# pcakages
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

# project
from usbills_app.db.models import Bill, BillSection
from usbills_app.logger import create_logger

# create logger
LOGGER = create_logger(__name__)


class BillQuery:
    """Class for bill querying functionality."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session

    async def get_by_package_id(self, package_id: str) -> Optional[Bill]:
        """Get bill by package ID.

        Args:
            package_id (str): Unique package identifier

        Returns:
            Optional[Bill]: Bill if found, None otherwise
        """
        stmt = select(Bill).filter(Bill.package_id == package_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[Bill]:
        """Get bill by slug.

        Args:
            slug (str): Unique bill slug

        Returns:
            Optional[Bill]: Bill if found, None otherwise
        """
        stmt = select(Bill).filter(Bill.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_title(
        self, query: str, limit: int = 100, offset: int = 0
    ) -> Sequence[Bill]:
        """Search bills by title using case-insensitive pattern matching.

        Args:
            query (str): Search query string
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of matching bills
        """
        stmt = (
            select(Bill)
            .filter(Bill.title.ilike(f"%{query}%"))
            .order_by(Bill.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_text(
        self, query: str, limit: int = 100, offset: int = 0
    ) -> Sequence[Bill]:
        """Search bills by full text using case-insensitive pattern matching.

        Args:
            query (str): Search query string
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of matching bills
        """
        stmt = (
            select(Bill)
            .filter(Bill.text.ilike(f"%{query}%"))
            .order_by(Bill.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_summary(self, query: str, limit: int = 100) -> Sequence[Bill]:
        """Search bills by summary using case-insensitive pattern matching.

        Args:
            query (str): Search query string
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of matching bills
        """
        stmt = (
            select(Bill)
            .filter(Bill.summary.ilike(f"%{query}%"))
            .order_by(Bill.date.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def match_keyword(
        self, keyword: str, limit: int = 100, offset: int = 0
    ) -> Sequence[Bill]:
        """Find bills that have exact match of keyword in their keywords array.

        Args:
            keyword (str): Keyword to match
            limit (int): Max number of bills to return
            offset (int): Offset for pagination

        Returns:
            Sequence[Bill]: List of matching bills
        """
        stmt = (
            select(Bill)
            .filter(Bill.keywords.contains([keyword]))
            .order_by(Bill.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def search_all(
        self, query: str, limit: int = 100, offset: int = 0
    ) -> Sequence[Bill]:
        """Search across title, text, summary and keywords.

        Args:
            query (str): Search query string
            limit (int): Max number of bills to return
            offset (int): Offset for pagination

        Returns:
            Sequence[Bill]: List of matching bills
        """
        stmt = (
            select(Bill)
            .filter(
                or_(
                    Bill.title.ilike(f"%{query}%"),
                    Bill.text.ilike(f"%{query}%"),
                    Bill.summary.ilike(f"%{query}%"),
                    Bill.keywords.contains([query]),
                )
            )
            .order_by(Bill.date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # Existing methods preserved...
    async def get_by_date(
        self,
        start_date: datetime.date,
        end_date: Optional[datetime.date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Bill]:
        """Get bills by date range.

        Args:
            start_date (datetime.date): Start date
            end_date (Optional[datetime.date]): End date (default: start_date)
            limit (int): Max number of bills to return
            offset (int): Offset for pagination

        Returns:
            Sequence[Bill]: List of bills in date range
        """
        if end_date is None:
            end_date = start_date

        stmt = (
            select(Bill)
            .filter(Bill.date >= start_date)
            .filter(Bill.date <= end_date)
            .order_by(Bill.date.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_congress(self, congress: str, limit: int = 100) -> Sequence[Bill]:
        """Get bills from specific Congress.

        Args:
            congress (str): Congress identifier
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of bills from Congress
        """
        stmt = (
            select(Bill)
            .filter(Bill.congress == congress)
            .order_by(Bill.date.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_bill_type(
        self, bill_type: str, limit: int = 100
    ) -> Sequence[Bill]:
        """Get bills of specific type.

        Args:
            bill_type (str): Bill type identifier
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of bills of type
        """
        stmt = (
            select(Bill)
            .filter(Bill.bill_type == bill_type)
            .order_by(Bill.date.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_chamber(self, chamber: str, limit: int = 100) -> Sequence[Bill]:
        """Get bills from specific chamber.

        Args:
            chamber (str): Chamber identifier ('house' or 'senate')
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of bills from chamber
        """
        stmt = (
            select(Bill)
            .filter(Bill.current_chamber == chamber)
            .order_by(Bill.date.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_legis_num(self, legis_num: str) -> Optional[Bill]:
        """Get bill by legislative number.

        Args:
            legis_num (str): Legislative number

        Returns:
            Optional[Bill]: Bill if found, None otherwise
        """
        stmt = select(Bill).filter(Bill.legis_num == legis_num)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_version(
        self, bill_version: str, limit: int = 100
    ) -> Sequence[Bill]:
        """Get bills of specific version.

        Args:
            bill_version (str): Bill version code
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of bills of version
        """
        stmt = (
            select(Bill)
            .filter(Bill.bill_version == bill_version)
            .order_by(Bill.date.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_appropriations(self, limit: int = 100) -> Sequence[Bill]:
        """Get appropriation bills.

        Args:
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of appropriation bills
        """
        stmt = (
            select(Bill)
            .filter(Bill.is_appropriation is True)
            .order_by(Bill.date.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_largest_bills(self, limit: int = 100) -> Sequence[Bill]:
        """Get largest bills by number of tokens.

        Args:
            limit (int): Max number of bills to return

        Returns:
            Sequence[Bill]: List of largest bills
        """
        stmt = select(Bill).order_by(Bill.num_tokens.desc()).limit(limit)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_newest_bills(
        self, limit: int = 100, offset: int = 0
    ) -> Sequence[Bill]:
        """Get most recent bills.

        Args:
            limit (int): Max number of bills to return
            offset (int): Offset for pagination

        Returns:
            Sequence[Bill]: List of most recent bills
        """
        # set up statement for both limit and offset
        stmt = (
            select(Bill)
            .order_by(Bill.date.desc())
            .order_by(Bill.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_old_bills(self, limit: int = 100, offset: int = 0) -> Sequence[Bill]:
        """Get oldest bills.

        Args:
            limit (int): Max number of bills to return
            offset (int): Offset for pagination

        Returns:
            Sequence[Bill]: List of oldest bills
        """
        # set up statement for both limit and offset
        stmt = select(Bill).order_by(Bill.date).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_bill_sections(self, bill: Bill) -> Sequence[BillSection]:
        """Get bill sections for a bill.

        Args:
            bill (Bill): Bill instance

        Returns:
            Sequence[BillSection]: List of bill sections
        """
        stmt = (
            select(BillSection)
            .filter(BillSection.bill_id == bill.id)
            .order_by(BillSection.id)
        )
        result = await self.session.execute(stmt)

        return result.scalars().all()
