"""
CLI task to load 1+ bill JSON files into the database.
"""

# imports
import argparse
import datetime
import gzip
import json
from pathlib import Path
from typing import Dict, Any

# packages
from sqlalchemy import select, func

# project
from usbills_app.db import Bill, BillSection, managed_async_session
from usbills_app.logger import create_logger
from usbills_app.utils.readability import get_ari_raw
from usbills_app.utils.slugs import get_default_slug

# create logger
LOGGER = create_logger(__name__)


def parse_bill_json(json_path: Path) -> Dict[str, Any]:
    """
    Parse a JSON file containing bill data.

    Args:
        json_path (Path): Path to the JSON file

    Returns:
        Dict[str, Any]: Parsed JSON data

    Raises:
        FileNotFoundError: If JSON file does not exist
        json.JSONDecodeError: If JSON parsing fails
    """
    LOGGER.debug("Attempting to parse JSON file: %s", json_path)

    if not json_path.exists():
        LOGGER.error("JSON file not found: %s", json_path)
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    try:
        with open(json_path, "rt", encoding="utf-8") as json_file:
            data = json.load(json_file)
            LOGGER.debug("Successfully parsed JSON file with %d keys", len(data))
            return data
    except Exception:
        # try as gzip json
        try:
            with gzip.open(json_path, "rb") as json_file:
                data = json.loads(json_file.read())
                LOGGER.debug("Successfully parsed JSON file with %d keys", len(data))
                return data
        except Exception as e:
            LOGGER.error("Failed to parse JSON file: %s - %s", json_path, str(e))
            raise


def create_bill_sections(
    bill: Bill, sections_data: list[Dict[str, Any]]
) -> list[BillSection]:
    """
    Create BillSection objects from section data.

    Args:
        bill (Bill): Parent Bill object
        sections_data (list[Dict[str, Any]]): List of section data dictionaries

    Returns:
        list[BillSection]: List of created BillSection objects
    """
    LOGGER.debug("Creating %d bill sections", len(sections_data))
    sections = []
    for i, section_data in enumerate(sections_data, 1):
        LOGGER.debug("Processing section %d/%d", i, len(sections_data))

        # calculate ari_raw
        ari_raw = get_ari_raw(
            {
                "num_characters": section_data.get("num_characters", 0),
                "num_tokens": section_data.get("num_tokens", 0),
                "num_sentences": section_data.get("num_sentences", 0),
            }
        )

        section = BillSection(
            bill=bill,
            enum=section_data.get("enum"),
            header=section_data.get("header"),
            toc_id=section_data.get("toc_id"),
            text=section_data.get("text", ""),
            markdown=section_data.get("markdown", ""),
            html=section_data.get("html", ""),
            num_tokens=section_data.get("num_tokens", 0),
            num_sentences=section_data.get("num_sentences", 0),
            num_characters=section_data.get("num_characters", 0),
            num_nouns=section_data.get("num_nouns", 0),
            num_verbs=section_data.get("num_verbs", 0),
            num_adjectives=section_data.get("num_adjectives", 0),
            num_adverbs=section_data.get("num_adverbs", 0),
            num_punctuations=section_data.get("num_punctuations", 0),
            num_numbers=section_data.get("num_numbers", 0),
            num_entities=section_data.get("num_entities", 0),
            avg_token_length=section_data.get("avg_token_length", 0.0),
            avg_sentence_length=section_data.get("avg_sentence_length", 0.0),
            token_entropy=section_data.get("token_entropy", 0.0),
            ari_raw=ari_raw,
            entities=section_data.get("entities", []),
            summary=section_data.get("summary"),
            issues=section_data.get("issues", []),
            money_sentences=section_data.get("money_sentences", []),
        )
        LOGGER.debug(
            "Created section with enum=%s, header=%s", section.enum, section.header
        )
        sections.append(section)
    return sections


def create_bill_from_json(json_path: Path) -> Bill:
    """
    Create a Bill object from a JSON file.

    Args:
        json_path (Path): Path to the JSON file

    Returns:
        Bill: Created Bill object
    """
    LOGGER.info("Creating Bill from JSON file: %s", json_path)

    # Parse JSON file
    try:
        data = parse_bill_json(json_path)
    except Exception as e:
        LOGGER.error("Failed to parse bill JSON: %s", str(e))
        raise

    LOGGER.debug("Creating Bill object from parsed data")

    # Create Bill object
    try:
        # calculate ari_raw
        ari_raw = get_ari_raw(
            {
                "num_characters": data.get("num_characters", 0),
                "num_tokens": data.get("num_tokens", 0),
                "num_sentences": data.get("num_sentences", 0),
            }
        )

        slug = get_default_slug(data["legis_num"], data["title"], data["bill_version"])

        bill = Bill(
            # Basic metadata
            title=data.get("title", ""),
            publisher=data.get("publisher", ""),
            date=datetime.datetime.fromisoformat(data.get("date")),
            congress=data.get("congress", ""),
            session=data.get("session", ""),
            legis_num=data.get("legis_num", ""),
            current_chamber=data.get("current_chamber", ""),
            is_appropriation=bool(data.get("is_appropriation", False)),
            bill_version=data.get("bill_version", ""),
            bill_type=data.get("bill_type", ""),
            package_id=data.get("package_id", ""),
            slug=slug,
            # Content fields
            text=data.get("text", ""),
            markdown=data.get("markdown", ""),
            html=data.get("html", ""),
            # Statistics
            num_pages=int(data.get("num_pages", 0)),
            num_sections=int(data.get("num_sections", 0)),
            num_tokens=int(data.get("num_tokens", 0)),
            num_sentences=int(data.get("num_sentences", 0)),
            num_characters=int(data.get("num_characters", 0)),
            num_nouns=int(data.get("num_nouns", 0)),
            num_verbs=int(data.get("num_verbs", 0)),
            num_adjectives=int(data.get("num_adjectives", 0)),
            num_adverbs=int(data.get("num_adverbs", 0)),
            num_punctuations=int(data.get("num_punctuations", 0)),
            num_numbers=int(data.get("num_numbers", 0)),
            num_entities=int(data.get("num_entities", 0)),
            # Averages
            avg_token_length=float(data.get("avg_token_length", 0.0)),
            avg_sentence_length=float(data.get("avg_sentence_length", 0.0)),
            token_entropy=float(data.get("token_entropy", 0.0)),
            ari_raw=ari_raw,
            # Analysis
            entities=data.get("entities", []),
            summary=data.get("summary"),
            commentary=data.get("commentary"),
            money_commentary=data.get("money_commentary"),
            eli5=data.get("eli5"),
            issues=data.get("issues", []),
            keywords=data.get("keywords", []),
            money_sentences=data.get("money_sentences", []),
            short_titles=data.get("short_titles", []),
            llm_model_id=data.get("llm_model_id", ""),
        )
        LOGGER.debug(
            "Created bill object for %s: congress=%s, legis_num=%s",
            bill.title[:50],
            bill.congress,
            bill.legis_num,
        )
    except Exception as e:
        LOGGER.error("Failed to create Bill object: %s", str(e))
        raise

    # Create sections if present
    if "sections" in data:
        LOGGER.debug("Creating bill sections")
        try:
            bill.sections = create_bill_sections(bill, data["sections"])
            LOGGER.debug("Created %d bill sections", len(bill.sections))
        except Exception as e:
            LOGGER.error("Failed to create bill sections: %s", str(e))
            raise
    else:
        LOGGER.warning("No sections data found in JSON file")

    LOGGER.info(
        "Successfully created Bill with %d sections for %s",
        len(bill.sections),
        bill.legis_num,
    )

    return bill


async def main():
    parser = argparse.ArgumentParser(description="Create Bill object from JSON file")
    parser.add_argument("json_path", type=Path, help="Path to the JSON file")
    args = parser.parse_args()

    # check if it's a folder of file
    async with managed_async_session() as session:
        if args.json_path.is_dir():
            for json_path in args.json_path.glob("*"):
                try:
                    LOGGER.info("Processing JSON file: %s", json_path)

                    # process the bill json
                    bill = create_bill_from_json(json_path)

                    # check if the bill exists in the session using package_id as unique key
                    # package_id is NOT the primary key
                    # select count from bills where package_id = bill.package_id
                    bill_statement = select(func.count(Bill.id)).filter(
                        Bill.package_id == bill.package_id
                    )
                    bill_exists = await session.execute(bill_statement)
                    if bill_exists.scalar() > 0:
                        LOGGER.info(
                            "Bill object package_id=%s already exists in database",
                            bill.package_id,
                        )
                        continue

                    session.add(bill)
                    for section in bill.sections:
                        session.add(section)
                    LOGGER.info("Bill object saved to database")
                    await session.commit()
                except Exception as e:
                    LOGGER.error("Failed to process JSON file: %s", str(e))
                    await session.rollback()
        else:
            # process single file
            LOGGER.info("Processing JSON file: %s", args.json_path)
            bill = create_bill_from_json(args.json_path)
            session.add(bill)
            for section in bill.sections:
                session.add(section)
            await session.commit()
            LOGGER.info("Bill object saved to database")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
