"""
Tests for text preprocessing functionality.
"""

import pytest
import sys
import os

# Add the parent directory to the path to import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing import TextPreprocessor, load_and_preprocess_dataset


class TestTextPreprocessor:
    """Test class for TextPreprocessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = TextPreprocessor()

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "Hello WORLD! This is a TEST."
        cleaned = self.preprocessor.clean_text(text)
        assert cleaned == "hello world this is a test"

    def test_clean_text_with_urls(self):
        """Test text cleaning with URLs."""
        text = "Check out https://example.com and http://test.org for more info"
        cleaned = self.preprocessor.clean_text(text)
        assert "https://example.com" not in cleaned
        assert "http://test.org" not in cleaned
        assert "check out" in cleaned

    def test_clean_text_with_mentions_and_hashtags(self):
        """Test text cleaning with mentions and hashtags."""
        text = "Hey @user check out #trending news today!"
        cleaned = self.preprocessor.clean_text(text)
        assert "@user" not in cleaned
        assert "#trending" not in cleaned
        assert "hey" in cleaned
        assert "news" in cleaned

    def test_clean_text_with_html_tags(self):
        """Test text cleaning with HTML tags."""
        text = "This is <b>bold</b> and <i>italic</i> text"
        cleaned = self.preprocessor.clean_text(text)
        assert "<b>" not in cleaned
        assert "</b>" not in cleaned
        assert "<i>" not in cleaned
        assert "</i>" not in cleaned
        assert "bold" in cleaned
        assert "italic" in cleaned

    def test_clean_text_with_extra_whitespace(self):
        """Test text cleaning with extra whitespace."""
        text = "This    has     multiple     spaces"
        cleaned = self.preprocessor.clean_text(text)
        assert cleaned == "this has multiple spaces"

    def test_clean_text_with_punctuation(self):
        """Test text cleaning with punctuation."""
        text = "Hello, world! How are you? I'm fine."
        cleaned = self.preprocessor.clean_text(text)
        assert "," not in cleaned
        assert "!" not in cleaned
        assert "?" not in cleaned
        assert "." not in cleaned
        assert "hello world how are you im fine" == cleaned

    def test_clean_text_empty_string(self):
        """Test cleaning empty string."""
        text = ""
        cleaned = self.preprocessor.clean_text(text)
        assert cleaned == ""

    def test_clean_text_non_string_input(self):
        """Test cleaning non-string input."""
        cleaned = self.preprocessor.clean_text(123)
        assert cleaned == ""

    def test_tokenize_for_training(self):
        """Test tokenization for training."""
        texts = ["Hello world", "How are you"]
        labels = [0, 1]
        
        tokenized, processed_labels = self.preprocessor.tokenize_for_training(texts, labels)
        
        assert 'input_ids' in tokenized
        assert 'attention_mask' in tokenized
        assert processed_labels == labels

    def test_tokenize_for_inference(self):
        """Test tokenization for inference."""
        text = "Hello world for inference"
        
        tokenized = self.preprocessor.tokenize_for_inference(text)
        
        assert 'input_ids' in tokenized
        assert 'attention_mask' in tokenized

    def test_get_word_importance_tokens(self):
        """Test getting word importance tokens."""
        text = "Breaking news: Scientists discover breakthrough"
        words = self.preprocessor.get_word_importance_tokens(text)
        
        assert isinstance(words, list)
        assert "breaking" in words
        assert "news" in words
        assert "scientists" in words

    def test_get_word_importance_tokens_empty_text(self):
        """Test getting word importance tokens from empty text."""
        text = ""
        words = self.preprocessor.get_word_importance_tokens(text)
        
        assert words == []


class TestDatasetLoading:
    """Test class for dataset loading functions."""

    def test_load_and_preprocess_dataset_default(self):
        """Test loading default sample dataset."""
        texts, labels = load_and_preprocess_dataset()
        
        assert isinstance(texts, list)
        assert isinstance(labels, list)
        assert len(texts) > 0
        assert len(labels) > 0
        assert len(texts) == len(labels)
        
        # Check that we have both fake and real news
        assert 0 in labels  # REAL
        assert 1 in labels  # FAKE

    def test_load_and_preprocess_dataset_content(self):
        """Test content of sample dataset."""
        texts, labels = load_and_preprocess_dataset()
        
        # Check that texts contain expected content
        fake_texts = [t for t, l in zip(texts, labels) if l == 1]
        real_texts = [t for t, l in zip(texts, labels) if l == 0]
        
        assert len(fake_texts) > 0
        assert len(real_texts) > 0
        
        # Check for fake news indicators
        fake_text_lower = " ".join(fake_texts).lower()
        assert any(indicator in fake_text_lower for indicator in ["breaking", "shocking", "miracle"])


if __name__ == "__main__":
    pytest.main([__file__])
