"""
SQLAlchemy model for bills.
"""

# package
from sqlalchemy import Boolean, Column, Date, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

# project
from usbills_app.db.models.base import Base
from usbills_app.db.models.constants import DEFAULT_FLOAT_VALUE


class Bill(Base):
    """SQLAlchemy model for bills.

    Represents a legislative bill with its metadata, content,
    and derived statistics from NLP analysis.
    """

    __tablename__ = "bills"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Basic metadata fields
    title = Column(String, nullable=False)
    publisher = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    congress = Column(String, nullable=False)
    session = Column(String, nullable=False)
    legis_num = Column(String, nullable=False)
    current_chamber = Column(String, nullable=False)
    is_appropriation = Column(Boolean, nullable=False, default=False)
    bill_version = Column(String, nullable=False)
    bill_type = Column(String, nullable=False)

    # Content fields
    text = Column(Text, nullable=False)
    markdown = Column(Text, nullable=False)
    html = Column(Text, nullable=False)

    # Document statistics
    num_pages = Column(Integer)
    num_sections = Column(Integer, nullable=False, default=0)
    num_tokens = Column(Integer, nullable=False, default=0)
    num_sentences = Column(Integer, nullable=False, default=0)
    num_characters = Column(Integer, nullable=False, default=0)
    num_nouns = Column(Integer, nullable=False, default=0)
    num_verbs = Column(Integer, nullable=False, default=0)
    num_adjectives = Column(Integer, nullable=False, default=0)
    num_adverbs = Column(Integer, nullable=False, default=0)
    num_punctuations = Column(Integer, nullable=False, default=0)
    num_numbers = Column(Integer, nullable=False, default=0)
    num_entities = Column(Integer, nullable=False, default=0)

    # Averages and statistics
    avg_token_length = Column(Float, nullable=False, default=DEFAULT_FLOAT_VALUE)
    avg_sentence_length = Column(Float, nullable=False, default=DEFAULT_FLOAT_VALUE)
    token_entropy = Column(Float, nullable=False, default=DEFAULT_FLOAT_VALUE)
    ari_raw = Column(Float, nullable=False, default=DEFAULT_FLOAT_VALUE)

    # Percentile values
    num_pages_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)
    num_sections_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)
    num_tokens_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)
    num_sentences_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)
    avg_token_length_percentile = Column(
        Float, nullable=True, default=DEFAULT_FLOAT_VALUE
    )
    avg_sentence_length_percentile = Column(
        Float, nullable=True, default=DEFAULT_FLOAT_VALUE
    )
    token_entropy_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)
    ari_raw_percentile = Column(Float, nullable=True, default=DEFAULT_FLOAT_VALUE)

    # Analysis fields
    entities = Column(ARRAY(String), default=list)
    money_sentences = Column(ARRAY(String), default=list)
    short_titles = Column(ARRAY(String), default=list)

    # LLM fields
    summary = Column(Text)
    commentary = Column(Text)
    money_commentary = Column(Text)
    eli5 = Column(Text)
    issues = Column(ARRAY(String), default=list)
    keywords = Column(ARRAY(String), default=list)

    # External references
    package_id = Column(String, unique=True)
    llm_model_id = Column(String)
    slug = Column(String, nullable=False, unique=True)

    # Relationships
    sections = relationship(
        "BillSection", back_populates="bill", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Return string representation of bill

        Returns:
            str: String representation of bill
        """
        return f"<Bill(id={self.id}, legis_num='{self.legis_num}')>"

    def to_dict(self) -> dict:
        """Return dictionary representation of bill

        Returns:
            dict: Dictionary representation of bill
        """
        return {
            "id": self.id,
            "title": self.title,
            "publisher": self.publisher,
            "date": self.date,
            "congress": self.congress,
            "session": self.session,
            "legis_num": self.legis_num,
            "current_chamber": self.current_chamber,
            "is_appropriation": self.is_appropriation,
            "bill_version": self.bill_version,
            "bill_type": self.bill_type,
            "text": self.text,
            "markdown": self.markdown,
            "html": self.html,
            "num_pages": self.num_pages,
            "num_sections": self.num_sections,
            "num_tokens": self.num_tokens,
            "num_sentences": self.num_sentences,
            "num_characters": self.num_characters,
            "num_nouns": self.num_nouns,
            "num_verbs": self.num_verbs,
            "num_adjectives": self.num_adjectives,
            "num_adverbs": self.num_adverbs,
            "num_punctuations": self.num_punctuations,
            "num_numbers": self.num_numbers,
            "num_entities": self.num_entities,
            "avg_token_length": self.avg_token_length,
            "avg_sentence_length": self.avg_sentence_length,
            "token_entropy": self.token_entropy,
            "ari_raw": self.ari_raw,
            "num_pages_percentile": self.num_pages_percentile,
            "num_sections_percentile": self.num_sections_percentile,
            "num_tokens_percentile": self.num_tokens_percentile,
            "num_sentences_percentile": self.num_sentences_percentile,
            "avg_token_length_percentile": self.avg_token_length_percentile,
            "avg_sentence_length_percentile": self.avg_sentence_length_percentile,
            "token_entropy_percentile": self.token_entropy_percentile,
            "ari_raw_percentile": self.ari_raw_percentile,
            "entities": self.entities,
            "money_sentences": self.money_sentences,
            "short_titles": self.short_titles,
            "summary": self.summary,
            "commentary": self.commentary,
            "money_commentary": self.money_commentary,
            "eli5": self.eli5,
            "issues": self.issues,
            "keywords": self.keywords,
            "package_id": self.package_id,
            "llm_model_id": self.llm_model_id,
            "slug": self.slug,
        }
