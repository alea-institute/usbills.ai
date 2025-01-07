"""Pydantic models for bill-related API requests and responses."""

# imports
import datetime
from typing import List, Optional, Dict

# packages
from pydantic import BaseModel, Field


class BillSlim(BaseModel):
    """Slim bill model for API responses."""

    # core metadata
    id: int = Field(..., description="Bill ID")
    package_id: str = Field(..., description="Package ID")
    title: str = Field(..., description="Bill title")
    publisher: str = Field(..., description="Bill publisher")
    date: datetime.date = Field(..., description="Bill publication date")
    congress: str = Field(..., description="Congress number")
    session: str = Field(..., description="Congressional session")
    legis_num: str = Field(..., description="Legislative number")
    current_chamber: str = Field(..., description="Current chamber")
    is_appropriation: bool = Field(..., description="Is appropriation bill")
    bill_version: str = Field(..., description="Bill version")
    bill_type: str = Field(..., description="Bill type")
    llm_model_id: str = Field(..., description="LLM model ID")
    slug: str = Field(..., description="Bill slug")
    api_url: Optional[str] = Field(..., description="API detail URL")

    # basic stats
    num_pages: int = Field(..., description="Number of pages")
    num_sections: int = Field(..., description="Number of sections")
    num_tokens: int = Field(..., description="Number of tokens")
    num_sentences: int = Field(..., description="Number of sentences")
    num_characters: int = Field(..., description="Number of characters")
    num_nouns: int = Field(..., description="Number of nouns")
    num_verbs: int = Field(..., description="Number of verbs")
    num_adjectives: int = Field(..., description="Number of adjectives")
    num_adverbs: int = Field(..., description="Number of adverbs")
    num_punctuations: int = Field(..., description="Number of punctuations")
    num_numbers: int = Field(..., description="Number of numbers")
    num_entities: int = Field(..., description="Number of entities")
    avg_token_length: float = Field(..., description="Average token length")
    avg_sentence_length: float = Field(..., description="Average sentence length")
    token_entropy: float = Field(..., description="Token entropy")
    ari_raw: float = Field(..., description="ARI raw score")

    # percentiles
    num_pages_percentile: float = Field(..., description="Num pages percentile")
    num_sections_percentile: float = Field(..., description="Num sections percentile")
    num_tokens_percentile: float = Field(..., description="Num tokens percentile")
    num_sentences_percentile: float = Field(..., description="Num sentences percentile")
    avg_token_length_percentile: float = Field(
        ..., description="Avg token length percentile"
    )
    avg_sentence_length_percentile: float = Field(
        ..., description="Avg sentence length percentile"
    )
    token_entropy_percentile: float = Field(..., description="Token entropy percentile")
    ari_raw_percentile: float = Field(..., description="ARI raw percentile")

    # other extracted information and llm outputs
    entities: List[str] = Field(..., description="List of entities")
    money_sentences: List[str] = Field(..., description="List of money sentences")
    short_titles: List[str] = Field(..., description="List of short titles")
    summary: str = Field(..., description="Bill summary")
    commentary: str = Field(..., description="Bill commentary")
    money_commentary: Optional[str] = Field(..., description="Money commentary")
    eli5: str = Field(..., description="Explain like I'm 5 summary")
    issues: List[str] = Field(..., description="List of issues")
    keywords: List[str] = Field(..., description="List of keywords")

    # set media type to json
    class Config:
        media_type = "application/json"


class BillSection(BaseModel):
    """
    Bill section model for API responses.
    """

    # core metadata
    id: int = Field(..., description="Section ID")
    bill_id: int = Field(..., description="Bill ID")
    enum: Optional[str] = Field(..., description="Section enum")
    header: Optional[str] = Field(..., description="Section header")
    toc_id: Optional[str] = Field(..., description="Table of contents ID")

    # stats
    num_tokens: int = Field(..., description="Number of tokens")
    num_sentences: int = Field(..., description="Number of sentences")
    num_characters: int = Field(..., description="Number of characters")
    num_nouns: int = Field(..., description="Number of nouns")
    num_verbs: int = Field(..., description="Number of verbs")
    num_adjectives: int = Field(..., description="Number of adjectives")
    num_adverbs: int = Field(..., description="Number of adverbs")
    num_punctuations: int = Field(..., description="Number of punctuations")
    num_numbers: int = Field(..., description="Number of numbers")
    num_entities: int = Field(..., description="Number of entities")
    avg_token_length: float = Field(..., description="Average token length")
    avg_sentence_length: float = Field(..., description="Average sentence length")
    token_entropy: float = Field(..., description="Token entropy")
    ari_raw: float = Field(..., description="ARI raw score")

    # content fields
    text: str = Field(..., description="Section text")
    markdown: str = Field(..., description="Section markdown")
    html: str = Field(..., description="Section HTML")

    # extractions and llm outputs
    entities: List[str] = Field(..., description="List of entities")
    summary: str = Field(..., description="Section summary")
    issues: List[str] = Field(..., description="List of issues")
    money_sentences: List[str] = Field(..., description="List of money sentences")


class BillFull(BaseModel):
    """Full bill model for API responses."""

    # core metadata
    id: int = Field(..., description="Bill ID")
    package_id: str = Field(..., description="Package ID")
    title: str = Field(..., description="Bill title")
    publisher: str = Field(..., description="Bill publisher")
    date: datetime.date = Field(..., description="Bill publication date")
    congress: str = Field(..., description="Congress number")
    session: str = Field(..., description="Congressional session")
    legis_num: str = Field(..., description="Legislative number")
    current_chamber: str = Field(..., description="Current chamber")
    is_appropriation: bool = Field(..., description="Is appropriation bill")
    bill_version: str = Field(..., description="Bill version")
    bill_type: str = Field(..., description="Bill type")
    llm_model_id: str = Field(..., description="LLM model ID")
    slug: str = Field(..., description="Bill slug")

    # basic stats
    num_pages: int = Field(..., description="Number of pages")
    num_sections: int = Field(..., description="Number of sections")
    num_tokens: int = Field(..., description="Number of tokens")
    num_sentences: int = Field(..., description="Number of sentences")
    num_characters: int = Field(..., description="Number of characters")
    num_nouns: int = Field(..., description="Number of nouns")
    num_verbs: int = Field(..., description="Number of verbs")
    num_adjectives: int = Field(..., description="Number of adjectives")
    num_adverbs: int = Field(..., description="Number of adverbs")
    num_punctuations: int = Field(..., description="Number of punctuations")
    num_numbers: int = Field(..., description="Number of numbers")
    num_entities: int = Field(..., description="Number of entities")
    avg_token_length: float = Field(..., description="Average token length")
    avg_sentence_length: float = Field(..., description="Average sentence length")
    token_entropy: float = Field(..., description="Token entropy")
    ari_raw: float = Field(..., description="ARI raw score")

    # percentiles
    num_pages_percentile: float = Field(..., description="Num pages percentile")
    num_sections_percentile: float = Field(..., description="Num sections percentile")
    num_tokens_percentile: float = Field(..., description="Num tokens percentile")
    num_sentences_percentile: float = Field(..., description="Num sentences percentile")
    avg_token_length_percentile: float = Field(
        ..., description="Avg token length percentile"
    )
    avg_sentence_length_percentile: float = Field(
        ..., description="Avg sentence length percentile"
    )
    token_entropy_percentile: float = Field(..., description="Token entropy percentile")
    ari_raw_percentile: float = Field(..., description="ARI raw percentile")

    # other extracted information and llm outputs
    entities: List[str] = Field(..., description="List of entities")
    money_sentences: List[str] = Field(..., description="List of money sentences")
    short_titles: List[str] = Field(..., description="List of short titles")
    summary: str = Field(..., description="Bill summary")
    commentary: str = Field(..., description="Bill commentary")
    money_commentary: Optional[str] = Field(..., description="Money commentary")
    eli5: str = Field(..., description="Explain like I'm 5 summary")
    issues: List[str] = Field(..., description="List of issues")
    keywords: List[str] = Field(..., description="List of keywords")

    # full content
    text: str = Field(..., description="Full bill text")
    markdown: str = Field(..., description="Full bill markdown")
    html: str = Field(..., description="Full bill HTML")

    # sections
    sections: List[BillSection] = Field(..., description="List of bill sections")

    # set media type to json
    class Config:
        media_type = "application/json"


class BillListSlim(BaseModel):
    """Model for paginated bill list responses."""

    total: int = Field(..., description="Total number of bills")
    bills: List[BillSlim] = Field(..., description="List of bills")

    # set media type to json
    class Config:
        media_type = "application/json"


class BillAggregateStats(BaseModel):
    """Model for bill aggregate statistics."""

    total_bills: int = Field(..., description="Total number of bills")
    total_sections: int = Field(..., description="Total number of sections")
    total_tokens: int = Field(..., description="Total number of tokens")
    total_sentences: int = Field(..., description="Total number of sentences")
    bills_by_type: Dict[str, float] = Field(
        ..., description="Distribution of bills by type"
    )
    bills_by_chamber: Dict[str, float] = Field(
        ..., description="Distribution of bills by chamber"
    )
    bills_by_version: Dict[str, float] = Field(
        ..., description="Distribution of bills by version"
    )
    token_stats: Dict[str, float] = Field(..., description="Token statistics")
    section_stats: Dict[str, float] = Field(..., description="Section statistics")
    entropy_stats: Dict[str, float] = Field(..., description="Entropy statistics")
