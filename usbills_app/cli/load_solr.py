"""
CLI task to load data into Solr from pg backend.
"""

# imports
import asyncio
from typing import List, Dict, Any

# packages
from sqlalchemy import select

# project
from usbills_app.db import Bill, managed_async_session
from usbills_app.utils.solr import SolrClient
from usbills_app.logger import create_logger

# get logger
logger = create_logger(__name__)


# Constants
BATCH_SIZE = 100


async def get_bills() -> List[Dict[str, Any]]:
    """Get all bills from PostgreSQL database.

    Returns:
        List[Dict[str, Any]]: List of bill records as dictionaries
    """
    logger.info("Fetching bills from database")
    async with managed_async_session() as session:
        stmt = select(Bill)
        result = await session.execute(stmt)
        bills = result.scalars().all()

        bill_docs = []
        for bill in bills:
            doc = {
                "package_id": bill.package_id,
                "title": bill.title,
                "publisher": bill.publisher,
                "date": f"{bill.date.isoformat()}T00:00:00Z",
                "congress": bill.congress,
                "session": bill.session,
                "legis_num": bill.legis_num,
                "current_chamber": bill.current_chamber,
                "is_appropriation": bill.is_appropriation,
                "bill_version": bill.bill_version,
                "bill_type": bill.bill_type,
                "text": bill.text,
                "markdown": bill.markdown,
                "html": bill.html,
                "num_pages": bill.num_pages,
                "num_sections": bill.num_sections,
                "num_tokens": bill.num_tokens,
                "num_sentences": bill.num_sentences,
                "num_characters": bill.num_characters,
                "num_nouns": bill.num_nouns,
                "num_verbs": bill.num_verbs,
                "num_adjectives": bill.num_adjectives,
                "num_adverbs": bill.num_adverbs,
                "num_punctuations": bill.num_punctuations,
                "num_numbers": bill.num_numbers,
                "num_entities": bill.num_entities,
                "avg_token_length": bill.avg_token_length,
                "avg_sentence_length": bill.avg_sentence_length,
                "token_entropy": bill.token_entropy,
                "entities": bill.entities,
                "money_sentences": bill.money_sentences,
                "short_titles": bill.short_titles,
                "issues": bill.issues,
                "keywords": bill.keywords,
                "summary": bill.summary,
                "commentary": bill.commentary,
                "money_commentary": bill.money_commentary,
                "eli5": bill.eli5,
                "llm_model_id": bill.llm_model_id,
            }
            bill_docs.append(doc)

        logger.info(f"Retrieved {len(bill_docs)} bills from database")
        return bill_docs


def update_solr(bills: List[Dict[str, Any]]) -> None:
    """Send bills to Solr for indexing.

    Args:
        bills: List of bill records to index
    """
    logger.info("Connecting to Solr")

    with SolrClient() as solr:
        # Delete all existing documents
        try:
            solr.delete_documents("fbs", "*:*")
            logger.info("Cleared existing Solr index")
        except Exception as e:
            logger.error(f"Failed to clear Solr index: {str(e)}")
            raise

        # Index in batches
        for i in range(0, len(bills), BATCH_SIZE):
            batch = bills[i : i + BATCH_SIZE]
            try:
                solr.add_documents("fbs", batch)
                solr.commit("fbs")
                logger.info(f"Indexed batch of {len(batch)} documents")
            except Exception as e:
                logger.error(f"Failed to index batch: {str(e)}")
                # Log problematic docs
                for doc in batch:
                    logger.error(f"Problem doc ID: {doc.get('package_id')}")
                raise


async def main() -> None:
    """Main entry point for script."""
    try:
        logger.info("Starting Solr update process")
        bills = await get_bills()
        update_solr(bills)
        logger.info("Successfully completed Solr update")
    except Exception as e:
        logger.error(f"Failed to update Solr: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
