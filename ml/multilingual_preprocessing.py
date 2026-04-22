"""
Multilingual text preprocessing utilities for fake news detection.
Supports English and Hindi languages.
"""

import re
import string
from typing import List, Tuple, Optional
import pandas as pd
from transformers import AutoTokenizer
import langdetect


class MultilingualTextPreprocessor:
    """Multilingual preprocessor for text data in fake news detection."""
    
    def __init__(self, model_name: str = "distilbert-base-multilingual-cased"):
        """
        Initialize the multilingual preprocessor.
        
        Args:
            model_name: Name of the pretrained multilingual model for tokenizer
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
        
        # Language-specific patterns
        self.hindi_pattern = re.compile(r'[\u0900-\u097F]')
        self.english_pattern = re.compile(r'[a-zA-Z]')
        
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the text.
        
        Args:
            text: Input text
            
        Returns:
            Detected language ('en', 'hi', or 'mixed')
        """
        try:
            detected = langdetect.detect(text)
            return detected
        except:
            # Fallback to pattern matching
            has_hindi = bool(self.hindi_pattern.search(text))
            has_english = bool(self.english_pattern.search(text))
            
            if has_hindi and has_english:
                return 'mixed'
            elif has_hindi:
                return 'hi'
            else:
                return 'en'
    
    def clean_text(self, text: str, language: Optional[str] = None) -> str:
        """
        Clean and preprocess multilingual text.
        
        Args:
            text: Input text to clean
            language: Optional language hint ('en', 'hi', 'mixed')
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
        
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)
        
        # Common cleaning for all languages
        text = text.strip()
        
        # Remove URLs (universal)
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove mentions and hashtags (universal)
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove HTML tags (universal)
        text = re.sub(r'<.*?>', '', text)
        
        # Language-specific cleaning
        if language == 'en':
            text = self._clean_english_text(text)
        elif language == 'hi':
            text = self._clean_hindi_text(text)
        elif language == 'mixed':
            text = self._clean_mixed_text(text)
        
        # Remove extra whitespace (universal)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _clean_english_text(self, text: str) -> str:
        """Clean English text."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove English punctuation (keep Hindi characters)
        english_punctuation = string.punctuation
        text = text.translate(str.maketrans('', '', english_punctuation))
        
        return text
    
    def _clean_hindi_text(self, text: str):
        """Clean Hindi text."""
        # Remove extra spaces between Hindi words
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common Hindi punctuation marks
        hindi_punctuation = '।॥॰'
        for punct in hindi_punctuation:
            text = text.replace(punct, '')
        
        return text
    
    def _clean_mixed_text(self, text: str) -> str:
        """Clean mixed English-Hindi text."""
        # Apply both cleaning methods
        text = self._clean_english_text(text)
        text = self._clean_hindi_text(text)
        
        return text
    
    def tokenize_for_training(self, texts: List[str], labels: List[int], 
                          languages: Optional[List[str]] = None,
                          max_length: int = 512) -> Tuple[dict, List[int]]:
        """
        Tokenize texts for training with language information.
        
        Args:
            texts: List of input texts
            labels: List of corresponding labels
            languages: Optional list of languages for each text
            max_length: Maximum sequence length
            
        Returns:
            Tuple of (tokenized_inputs, labels)
        """
        # Clean texts with language detection
        cleaned_texts = []
        detected_languages = []
        
        for i, text in enumerate(texts):
            lang = languages[i] if languages else None
            cleaned_text = self.clean_text(text, lang)
            cleaned_texts.append(cleaned_text)
            
            # Store detected language for analysis
            detected_lang = self.detect_language(text)
            detected_languages.append(detected_lang)
        
        # Tokenize
        tokenized_inputs = self.tokenizer(
            cleaned_texts,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        return tokenized_inputs, labels, detected_languages
    
    def tokenize_for_inference(self, text: str, language: Optional[str] = None, 
                            max_length: int = 512) -> dict:
        """
        Tokenize single text for inference.
        
        Args:
            text: Input text
            language: Optional language hint
            max_length: Maximum sequence length
            
        Returns:
            Tokenized input
        """
        cleaned_text = self.clean_text(text, language)
        
        tokenized_input = self.tokenizer(
            cleaned_text,
            truncation=True,
            padding=True,
            max_length=max_length,
            return_tensors="pt"
        )
        
        return tokenized_input
    
    def get_word_importance_tokens(self, text: str, language: Optional[str] = None) -> List[str]:
        """
        Get individual words for explainability analysis (language-aware).
        
        Args:
            text: Input text
            language: Optional language hint
            
        Returns:
            List of words
        """
        cleaned_text = self.clean_text(text, language)
        
        # Language-specific tokenization
        if language == 'hi' or (language is None and self.detect_language(text) == 'hi'):
            # Hindi text - split on spaces (Hindi doesn't use spaces between all words traditionally)
            words = [word for word in cleaned_text.split() if word.strip()]
        else:
            # English or mixed - standard word splitting
            words = cleaned_text.split()
        
        return [word for word in words if word]
    
    def analyze_text_statistics(self, texts: List[str]) -> dict:
        """
        Analyze language distribution in a dataset.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Dictionary with language statistics
        """
        language_counts = {'en': 0, 'hi': 0, 'mixed': 0, 'other': 0}
        
        for text in texts:
            lang = self.detect_language(text)
            if lang in language_counts:
                language_counts[lang] += 1
            else:
                language_counts['other'] += 1
        
        total = len(texts)
        language_percentages = {
            lang: (count / total) * 100 for lang, count in language_counts.items()
        }
        
        return {
            'counts': language_counts,
            'percentages': language_percentages,
            'total_texts': total
        }


def load_multilingual_dataset(data_path: str = None) -> Tuple[List[str], List[int], List[str]]:
    """
    Load and preprocess a multilingual dataset.
    
    Args:
        data_path: Path to dataset file
        
    Returns:
        Tuple of (texts, labels, languages)
    """
    # Create sample multilingual data if no dataset provided
    if data_path is None:
        # Sample fake news data in multiple languages
        fake_news = [
            "Breaking: Scientists discover cure for all diseases overnight!",
            "शॉकिंग: वैज्ञानिकों ने एक रात में सभी बीमारियों का इलाज खोजा!",
            "SHOCKING: Government hiding truth about aliens for 50 years!",
            "खबरदार: सरकार 50 साल से एलियंस के बारे में सच छुपा रही है!",
            "Miracle weight loss pill melts fat while you sleep - doctors hate this!",
            "चमत्कार वजन घटाने वाली गोली सोते समय वसा को पिघला देती है!",
        ]
        
        real_news = [
            "Federal Reserve announces interest rate decision following economic meeting",
            "फेडरल रिजर्व ने आर्थिक बैठक के बाद ब्याज दर का फैसला किया",
            "Local elections scheduled for November with several candidates running",
            "स्थानीय चुनाव नवंबर के लिए निर्धारित, कई उम्मीदवार चुनाव लड़ रहे",
            "Tech company reports quarterly earnings exceeding analyst expectations",
            "तकनीकी कंपनी की त्रैमासिक कमाई विश्लेषकों की अपेक्षा से अधिक",
        ]
        
        texts = fake_news + real_news
        labels = [1] * len(fake_news) + [0] * len(real_news)  # 1=FAKE, 0=REAL
        
        # Detect languages
        preprocessor = MultilingualTextPreprocessor()
        languages = [preprocessor.detect_language(text) for text in texts]
        
    else:
        # Load actual dataset
        df = pd.read_csv(data_path)
        # Assuming dataset has 'text', 'label', and optionally 'language' columns
        texts = df['text'].tolist()
        labels = df['label'].tolist()
        
        if 'language' in df.columns:
            languages = df['language'].tolist()
        else:
            preprocessor = MultilingualTextPreprocessor()
            languages = [preprocessor.detect_language(text) for text in texts]
    
    return texts, labels, languages
