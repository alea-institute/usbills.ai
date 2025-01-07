"""
CLI script to update percentile values for all bills in the database.
"""

# imports
import asyncio
from typing import Dict

# packages
from sqlalchemy import select, update

# project
from usbills_app.db import Bill, managed_async_session
from usbills_app.logger import create_logger

# create logger
LOGGER = create_logger(__name__)


async def calculate_percentiles(session, column_name: str) -> Dict[int, float]:
    """
    Calculate percentile ranks for a given column across all bills.

    Args:
        session: SQLAlchemy async session
        column_name: Name of the column to calculate percentiles for

    Returns:
        Dict mapping bill ID to percentile value
    """
    # Get the actual column object
    column = getattr(Bill, column_name)

    # Get all bill IDs and values for this column
    stmt = select(Bill.id, column)
    result = await session.execute(stmt)
    rows = result.all()

    # Convert to list of values
    values = [row[1] for row in rows]
    total = len(values)

    # Calculate percentiles for each value
    percentiles = {}
    for bill_id, value in rows:
        # Count how many values are less than this one
        rank = sum(1 for v in values if v < value)
        percentile = (rank / total) * 100.0
        percentiles[bill_id] = percentile

    return percentiles


async def update_percentiles(session) -> None:
    """
    Update all percentile columns for all bills in database.

    Args:
        session: SQLAlchemy async session
    """
    # List of columns to calculate percentiles for
    percentile_columns = [
        ("num_pages", "num_pages_percentile"),
        ("num_sections", "num_sections_percentile"),
        ("num_tokens", "num_tokens_percentile"),
        ("num_sentences", "num_sentences_percentile"),
        ("avg_token_length", "avg_token_length_percentile"),
        ("avg_sentence_length", "avg_sentence_length_percentile"),
        ("token_entropy", "token_entropy_percentile"),
        ("ari_raw", "ari_raw_percentile"),
    ]

    for source_col, target_col in percentile_columns:
        LOGGER.info(f"Calculating percentiles for {source_col}")

        # Calculate percentiles
        percentiles = await calculate_percentiles(session, source_col)

        # Update each bill
        for bill_id, percentile in percentiles.items():
            stmt = (
                update(Bill).where(Bill.id == bill_id).values({target_col: percentile})
            )
            await session.execute(stmt)

        await session.commit()
        LOGGER.info(f"Updated {len(percentiles)} bills for {target_col}")


async def main() -> None:
    """Main entry point for script."""
    LOGGER.info("Starting percentile update")

    async with managed_async_session() as session:
        await update_percentiles(session)

    LOGGER.info("Completed percentile update")


if __name__ == "__main__":
    asyncio.run(main())
