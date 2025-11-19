"""
StrOrigin Change Analysis - Phase 2.3

This module provides functions to analyze StrOrigin changes in VRS data:
1. Punctuation/space-only detection
2. Semantic similarity calculation using Korean BERT

Author: Neil Schmitt
Version: 1119.0
"""

import re
import unicodedata
import os
import numpy as np
from typing import Optional, Tuple


def normalize_text_for_comparison(text: str) -> str:
    """
    Remove all spaces and punctuation for punctuation/space-only comparison.

    This function strips out all whitespace and punctuation marks (including
    Korean, Japanese, and Chinese punctuation) to determine if two texts differ
    only in formatting, not content.

    Args:
        text: Input text to normalize

    Returns:
        Normalized text with spaces and punctuation removed, lowercased

    Examples:
        >>> normalize_text_for_comparison("안녕하세요!")
        '안녕하세요'
        >>> normalize_text_for_comparison("Hello, world!")
        'helloworld'
    """
    if not isinstance(text, str):
        return ""

    # Remove all whitespace
    text = re.sub(r'\s+', '', text)

    # Remove all punctuation (including Korean, Japanese, Chinese punctuation)
    # Unicode categories starting with 'P' are punctuation
    text = ''.join(char for char in text if not unicodedata.category(char).startswith('P'))

    # Case-insensitive comparison
    return text.lower()


def is_punctuation_space_change_only(prev_text: str, curr_text: str) -> bool:
    """
    Check if two texts differ only in punctuation or whitespace.

    Args:
        prev_text: Previous StrOrigin text
        curr_text: Current StrOrigin text

    Returns:
        True if texts are identical after removing spaces/punctuation, False otherwise

    Examples:
        >>> is_punctuation_space_change_only("안녕하세요", "안녕하세요!")
        True
        >>> is_punctuation_space_change_only("Hello", "Goodbye")
        False
    """
    normalized_prev = normalize_text_for_comparison(prev_text)
    normalized_curr = normalize_text_for_comparison(curr_text)

    return normalized_prev == normalized_curr


def calculate_semantic_similarity(text1: str, text2: str, model) -> float:
    """
    Calculate semantic similarity between two texts using BERT embeddings.

    Uses cosine similarity on BERT-generated embeddings to determine how
    semantically similar two texts are, regardless of exact wording.

    Args:
        text1: First text to compare
        text2: Second text to compare
        model: Loaded SentenceTransformer model

    Returns:
        Similarity score between 0.0 and 1.0 (0% to 100%)

    Examples:
        >>> # Assuming model is loaded
        >>> calculate_semantic_similarity("안녕하세요", "안녕", model)
        0.85  # 85% similar
    """
    if not text1 or not text2:
        return 0.0

    # Encode both texts to get embeddings
    embeddings = model.encode([text1, text2], convert_to_numpy=True)

    # Calculate cosine similarity
    # Cosine similarity = dot product / (norm1 * norm2)
    embedding1 = embeddings[0]
    embedding2 = embeddings[1]

    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)

    # Clamp to [0, 1] range (cosine similarity can theoretically be negative)
    similarity = max(0.0, min(1.0, similarity))

    return similarity


class StrOriginAnalyzer:
    """
    Analyzer for StrOrigin changes combining punctuation detection and BERT similarity.

    This class handles the full analysis pipeline:
    1. First Pass: Check if change is punctuation/space only
    2. Second Pass: Calculate semantic similarity using BERT if not punctuation-only

    The model is loaded lazily (only when first needed) for performance.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the analyzer.

        Args:
            model_path: Path to BERT model directory. If None, uses default project path.
        """
        self.model = None
        self.model_path = model_path or self._get_default_model_path()

    def _get_default_model_path(self) -> str:
        """Get default model path relative to project root"""
        # Get project root (assuming this file is in src/utils/)
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        return os.path.join(project_root, 'models', 'kr-sbert')

    def _load_model(self):
        """
        Lazy load the BERT model (only when first needed).

        Attempts to load in this order:
        1. Online from Hugging Face (auto-downloads if needed) - DEFAULT
        2. Offline from local cache (fallback if no internet)
        3. Raises FileNotFoundError if both fail
        """
        if self.model is not None:
            return

        from sentence_transformers import SentenceTransformer

        model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'

        # Try 1: Load from Hugging Face (online mode - AUTO-DOWNLOAD)
        try:
            print(f"  → Attempting to load BERT model from Hugging Face (online mode)...")
            self.model = SentenceTransformer(model_name)
            print(f"  ✓ Model loaded successfully from Hugging Face")
            return
        except Exception as e:
            print(f"  ℹ️  Online mode unavailable: {str(e)[:100]}")
            print(f"  → Trying local cache...")

        # Try 2: Load from local cache (offline mode)
        if os.path.exists(self.model_path):
            try:
                self.model = SentenceTransformer(self.model_path)
                print(f"  ✓ Model loaded from local cache: {self.model_path}")
                return
            except Exception as e:
                print(f"  ⚠️  Failed to load local model: {e}")

        # Both failed - raise error with clear instructions
        raise FileNotFoundError(
            f"BERT model not available. Tried:\n"
            f"  1. Online from Hugging Face (no internet or connection failed)\n"
            f"  2. Local cache at {self.model_path} (not found)\n"
            f"\nFor offline use, run: download_model.bat"
        )

    def analyze(self, prev_text: str, curr_text: str) -> str:
        """
        Analyze the difference between previous and current StrOrigin texts.

        Returns one of:
        - "Punctuation/Space Change" - Only formatting differs
        - "XX.XX% similar" - Semantic similarity percentage (e.g., "94.5% similar")

        Args:
            prev_text: Previous StrOrigin text
            curr_text: Current StrOrigin text

        Returns:
            Analysis result string
        """
        # First Pass: Check punctuation/space only
        if is_punctuation_space_change_only(prev_text, curr_text):
            return "Punctuation/Space Change"

        # Second Pass: BERT semantic similarity
        self._load_model()  # Lazy load

        similarity = calculate_semantic_similarity(prev_text, curr_text, self.model)

        # Format as percentage with 1 decimal place
        similarity_pct = similarity * 100
        return f"{similarity_pct:.1f}% similar"

    def analyze_batch(self, text_pairs: list) -> list:
        """
        Analyze multiple text pairs efficiently.

        Args:
            text_pairs: List of (prev_text, curr_text) tuples

        Returns:
            List of analysis result strings
        """
        results = []

        for prev_text, curr_text in text_pairs:
            result = self.analyze(prev_text, curr_text)
            results.append(result)

        return results
