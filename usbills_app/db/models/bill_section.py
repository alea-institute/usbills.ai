"""
BillSection model for SQLAlchemy ORM.
"""

# packages
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

# project
from usbills_app.db.models.base import Base
from usbills_app.db.models.constants import DEFAULT_FLOAT_VALUE


class BillSection(Base):
    """SQLAlchemy model for bill sections.

    Represents a section within a bill, including the text content,
    parsed metadata, and NLP-derived statistics.
    """

    __tablename__ = "bill_sections"

    # Primary key and foreign key
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)

    # Section metadata
    enum = Column(String)
    header = Column(String)
    toc_id = Column(String)

    # Content fields
    text = Column(Text, nullable=False)
    markdown = Column(Text, nullable=False)
    html = Column(Text, nullable=False)

    # NLP statistics
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

    # Entity and analysis fields
    entities = Column(ARRAY(String), default=list)
    summary = Column(Text)
    issues = Column(ARRAY(String), default=list)
    money_sentences = Column(ARRAY(String), default=list)

    # Relationships
    bill = relationship("Bill", back_populates="sections")

    def __repr__(self) -> str:
        """Return string representation of section

        Returns:
            str: String representation of section
        """
        return f"<BillSection(id={self.id}, header='{self.header}')>"

    def to_dict(self) -> dict:
        """Return dictionary representation of section

        Returns:
            dict: Dictionary representation of section
        """
        return {
            "id": self.id,
            "bill_id": self.bill_id,
            "enum": self.enum,
            "header": self.header,
            "toc_id": self.toc_id,
            "text": self.text,
            "markdown": self.markdown,
            "html": self.html,
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
            "entities": self.entities,
            "summary": self.summary,
            "issues": self.issues,
            "money_sentences": self.money_sentences,
        }
