"""
StrOrigin Change Analysis - Phase 2.3

This module provides functions to analyze StrOrigin changes in VRS data:
1. Punctuation/space-only detection
2. Semantic similarity calculation using Korean BERT
3. Character-level diff highlighting (shows exact changes)

Author: Neil Schmitt
Version: 1121.0
"""

import re
import unicodedata
import os
import numpy as np
from difflib import SequenceMatcher
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


def extract_differences(text1: str, text2: str, max_length: int = 80) -> str:
    """
    Extract WORD-LEVEL differences between two texts using difflib.

    Shows exactly what changed in WinMerge style with automatic chunking:
    - [old words→new words] for replacements (consecutive words grouped)
    - [-deleted words] for deletions
    - [+added words] for additions

    Args:
        text1: Previous text
        text2: Current text
        max_length: Maximum length for diff output (truncate if longer)

    Returns:
        Diff string showing changes, or empty string if no changes

    Examples:
        >>> extract_differences("Hello world", "Hallo world")
        '[Hello→Hallo]'
        >>> extract_differences("Press any button", "Press button")
        '[-any]'
        >>> extract_differences("Loading", "Loading complete")
        '[+complete]'
        >>> extract_differences("The player won the game", "The enemy lost the battle")
        '[player won→enemy lost] [game→battle]'
    """
    if not text1 or not text2:
        return ""

    # Split into words (preserves Korean and English spacing)
    words1 = text1.split()
    words2 = text2.split()

    # Word-level diff (automatic chunking of consecutive changes)
    matcher = SequenceMatcher(None, words1, words2)
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            old_words = ' '.join(words1[i1:i2])
            new_words = ' '.join(words2[j1:j2])
            changes.append(f"[{old_words}→{new_words}]")
        elif tag == 'delete':
            deleted_words = ' '.join(words1[i1:i2])
            changes.append(f"[-{deleted_words}]")
        elif tag == 'insert':
            added_words = ' '.join(words2[j1:j2])
            changes.append(f"[+{added_words}]")

    if not changes:
        return ""

    diff_str = ' '.join(changes)

    # Truncate if too long (avoid huge Excel cells)
    if len(diff_str) > max_length:
        diff_str = diff_str[:max_length-3] + "..."

    return diff_str


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

    Supports both LIGHT and FULL versions:
    - LIGHT: Punctuation/Space detection only (no BERT)
    - FULL: Punctuation/Space + BERT semantic similarity

    This class handles the full analysis pipeline:
    1. First Pass: Check if change is punctuation/space only (both versions)
    2. Second Pass: Calculate semantic similarity using BERT (FULL version only)

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
        self.bert_available = self._check_bert_available()

    def _get_default_model_path(self) -> str:
        """Get default model path relative to project root"""
        # Get project root (assuming this file is in src/utils/)
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        return os.path.join(project_root, 'models', 'kr-sbert')

    def _check_bert_available(self) -> bool:
        """
        Check if BERT packages are available.

        Returns:
            True if FULL version (torch + sentence_transformers available)
            False if LIGHT version (packages not available)
        """
        try:
            import torch
            import sentence_transformers
            return True
        except ImportError:
            return False

    def _load_model(self):
        """
        Lazy load the BERT model (only when first needed).

        Attempts to load in this order:
        1. Offline from bundled model (for FULL version .exe) - PRIORITY
        2. Online from Hugging Face (fallback if bundled not found)
        3. Raises FileNotFoundError if both fail
        """
        if self.model is not None:
            return

        from sentence_transformers import SentenceTransformer

        model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'

        # Try 1: Load from bundled local path (offline mode - PRIORITY)
        # This ensures the FULL version .exe works 100% offline
        if os.path.exists(self.model_path):
            try:
                print(f"  → Loading BERT model from bundled path (offline mode)...")
                self.model = SentenceTransformer(self.model_path)
                print(f"  ✓ Model loaded successfully from: {self.model_path}")
                return
            except Exception as e:
                print(f"  ⚠️  Failed to load bundled model: {e}")
                print(f"  → Trying online fallback...")

        # Try 2: Load from Hugging Face (online fallback)
        # Only if bundled model not found (e.g., running from source code)
        try:
            print(f"  → Attempting to load BERT model from Hugging Face (online mode)...")
            self.model = SentenceTransformer(model_name)
            print(f"  ✓ Model loaded successfully from Hugging Face")
            return
        except Exception as e:
            print(f"  ℹ️  Online mode unavailable: {str(e)[:100]}")

        # Both failed - raise error with clear instructions
        raise FileNotFoundError(
            f"BERT model not available. Tried:\n"
            f"  1. Bundled local model at {self.model_path} (not found)\n"
            f"  2. Online from Hugging Face (no internet or connection failed)\n"
            f"\nFor offline use, run: python scripts/download_bert_model.py"
        )

    def analyze(self, prev_text: str, curr_text: str) -> Tuple[str, str]:
        """
        Analyze the difference between previous and current StrOrigin texts.

        Returns a tuple of (analysis, diff_detail):
        - analysis: "Punctuation/Space Change", "XX.X% similar" (FULL), or "Content Change" (LIGHT)
        - diff_detail: "[old→new]" showing exact word-level changes, or "" if punctuation-only

        Args:
            prev_text: Previous StrOrigin text
            curr_text: Current StrOrigin text

        Returns:
            Tuple of (analysis_result, diff_detail)

        Examples:
            >>> analyzer.analyze("Hello", "Hallo")
            ("81.7% similar", "[Hello→Hallo]")
            >>> analyzer.analyze("Hello!", "Hello")
            ("Punctuation/Space Change", "")
        """
        # First Pass: Check punctuation/space only (works in both LIGHT and FULL)
        if is_punctuation_space_change_only(prev_text, curr_text):
            return ("Punctuation/Space Change", "")

        # Extract word-level differences
        diff_detail = extract_differences(prev_text, curr_text)

        # Second Pass: BERT semantic similarity (FULL version only)
        if self.bert_available:
            # FULL version: Calculate BERT similarity
            self._load_model()  # Lazy load
            similarity = calculate_semantic_similarity(prev_text, curr_text, self.model)
            similarity_pct = similarity * 100
            analysis = f"{similarity_pct:.1f}% similar"
        else:
            # LIGHT version: Can't calculate similarity
            analysis = "Content Change"

        return (analysis, diff_detail)

    def analyze_batch(self, text_pairs: list) -> list:
        """
        Analyze multiple text pairs efficiently.

        Args:
            text_pairs: List of (prev_text, curr_text) tuples

        Returns:
            List of (analysis, diff_detail) tuples
        """
        results = []

        for prev_text, curr_text in text_pairs:
            analysis, diff_detail = self.analyze(prev_text, curr_text)
            results.append((analysis, diff_detail))

        return results
