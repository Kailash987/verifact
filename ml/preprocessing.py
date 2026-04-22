"""
Text preprocessing utilities for fake news detection.
"""

import re
import string
from typing import List, Tuple
import pandas as pd
from transformers import AutoTokenizer


class TextPreprocessor:
    """Preprocessor for text data in fake news detection."""
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        """
        Initialize the preprocessor.
        
        Args:
            model_name: Name of the pretrained model for tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
        
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text.
        
        Args:
            text: Input text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove punctuation but keep sentence structure
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        return text
    
    def tokenize_for_training(self, texts: List[str], labels: List[int], 
                            max_length: int = 512) -> Tuple[dict, List[int]]:
        """
        Tokenize texts for training.
        
        Args:
            texts: List of input texts
            labels: List of corresponding labels
            max_length: Maximum sequence length
            
        Returns:
            Tuple of (tokenized_inputs, labels)
        """
        # Clean texts
        cleaned_texts = [self.clean_text(text) for text in texts]
        
        # Tokenize
        tokenized_inputs = self.tokenizer(
            cleaned_texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        return tokenized_inputs, labels
    
    def tokenize_for_inference(self, text: str, max_length: int = 512) -> dict:
        """
        Tokenize single text for inference.
        
        Args:
            text: Input text
            max_length: Maximum sequence length
            
        Returns:
            Tokenized input
        """
        cleaned_text = self.clean_text(text)
        
        tokenized_input = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        return tokenized_input
    
    def get_word_importance_tokens(self, text: str) -> List[str]:
        """
        Get individual words for explainability analysis.
        
        Args:
            text: Input text
            
        Returns:
            List of words
        """
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        return words


def load_and_preprocess_dataset(data_path: str = None) -> Tuple[List[str], List[int]]:
    """
    Load and preprocess a sample dataset.
    
    Args:
        data_path: Path to dataset file
        
    Returns:
        Tuple of (texts, labels)
    """
    # Create sample data if no dataset provided
    if data_path is None:
        # Sample fake news data for demonstration
        fake_news = [
            "Breaking: Scientists discover cure for all diseases overnight!",
            "SHOCKING: Government hiding truth about aliens for 50 years!",
            "Miracle weight loss pill melts fat while you sleep - doctors hate this!",
            "Celebrity caught in scandal that will end their career forever!",
            "Secret ancient remedy reverses aging in just 7 days!",
            "Conspiracy confirmed: Moon landing was faked by Hollywood!",
            "Breaking news: Economy will collapse next week - prepare now!",
            "Shocking revelation: Popular food causes cancer, cover-up exposed!",
        ]
        
        real_news = [
            "Federal Reserve announces interest rate decision following economic meeting",
            "Scientists publish new research on climate change impacts in Nature journal",
            "Local elections scheduled for November with several candidates running",
            "Tech company reports quarterly earnings exceeding analyst expectations",
            "Health officials provide update on vaccination campaign progress",
            "University study shows correlation between exercise and mental health",
            "Government announces infrastructure investment plan for rural areas",
            "Stock market closes mixed as investors await inflation data",
        ]
        
        texts = fake_news + real_news
        labels = [1] * len(fake_news) + [0] * len(real_news)  # 1=FAKE, 0=REAL
        
    else:
        # Load actual dataset
        df = pd.read_csv(data_path)
        # Assuming dataset has 'text' and 'label' columns
        texts = df['text'].tolist()
        labels = df['label'].tolist()
    
    return texts, labels
