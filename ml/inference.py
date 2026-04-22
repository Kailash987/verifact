"""
Inference module for fake news detection with explainability.
"""

import os
import torch
import numpy as np
import lime
import lime.lime_text
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import Dict, List, Tuple, Optional
import json
from preprocessing import TextPreprocessor


class FakeNewsPredictor:
    """Fake news predictor with explainability features."""
    
    def __init__(self, model_path: str = "ml/model/best_model"):
        """
        Initialize the predictor.
        
        Args:
            model_path: Path to the trained model
        """
        self.model_path = model_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load model and tokenizer
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Move model to device
        self.model.to(self.device)
        self.model.eval()
        
        # Initialize preprocessor
        self.preprocessor = TextPreprocessor()
        
        # Initialize LIME explainer
        self.lime_explainer = lime.lime_text.LimeTextExplainer(
            class_names=['REAL', 'FAKE'],
            random_state=42
        )
        
        # Label mapping
        self.label_map = {0: 'REAL', 1: 'FAKE'}
        
    def predict_single(self, text: str, return_probabilities: bool = True) -> Dict:
        """
        Predict single text input.
        
        Args:
            text: Input text to classify
            return_probabilities: Whether to return class probabilities
            
        Returns:
            Dictionary with prediction results
        """
        # Preprocess and tokenize
        tokenized_input = self.preprocessor.tokenize_for_inference(text)
        
        # Move to device
        input_ids = tokenized_input['input_ids'].to(self.device)
        attention_mask = tokenized_input['attention_mask'].to(self.device)
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probabilities, dim=-1).item()
            confidence = probabilities[0][predicted_class].item()
        
        result = {
            'text': text,
            'label': self.label_map[predicted_class],
            'confidence': round(confidence, 4),
            'predicted_class_id': predicted_class
        }
        
        if return_probabilities:
            result['probabilities'] = {
                'REAL': round(probabilities[0][0].item(), 4),
                'FAKE': round(probabilities[0][1].item(), 4)
            }
        
        return result
    
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """
        Predict multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of prediction results
        """
        results = []
        for text in texts:
            result = self.predict_single(text)
            results.append(result)
        
        return results
    
    def explain_prediction_lime(self, text: str, num_features: int = 10) -> Dict:
        """
        Explain prediction using LIME.
        
        Args:
            text: Input text to explain
            num_features: Number of features to include in explanation
            
        Returns:
            Dictionary with explanation results
        """
        # Get prediction first
        prediction = self.predict_single(text)
        
        # Define prediction function for LIME
        def predict_fn(texts):
            predictions = []
            for t in texts:
                pred = self.predict_single(t, return_probabilities=True)
                # Return probabilities for both classes
                predictions.append([pred['probabilities']['REAL'], pred['probabilities']['FAKE']])
            return np.array(predictions)
        
        # Generate explanation
        explanation = self.lime_explainer.explain_instance(
            text_instance=text,
            classifier_fn=predict_fn,
            num_features=num_features,
            num_samples=1000
        )
        
        # Extract important words and their weights
        important_words = []
        word_weights = []
        
        for feature, weight in explanation.as_list():
            important_words.append(feature)
            word_weights.append(weight)
        
        # Get explanation for predicted class
        predicted_class = prediction['predicted_class_id']
        class_explanation = explanation.as_list(label=predicted_class)
        
        result = {
            'text': text,
            'prediction': prediction,
            'explanation': {
                'method': 'LIME',
                'important_words': important_words,
                'word_weights': dict(zip(important_words, word_weights)),
                'class_explanation': class_explanation,
                'num_features': num_features
            }
        }
        
        return result
    
    def get_attention_weights(self, text: str) -> Dict:
        """
        Get attention weights for explainability.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with attention information
        """
        # Preprocess and tokenize
        tokenized_input = self.preprocessor.tokenize_for_inference(text)
        
        # Move to device
        input_ids = tokenized_input['input_ids'].to(self.device)
        attention_mask = tokenized_input['attention_mask'].to(self.device)
        
        # Get prediction with attention
        with torch.no_grad():
            outputs = self.model(
                input_ids=input_ids, 
                attention_mask=attention_mask,
                output_attentions=True
            )
            
            # Get attention weights (average across all heads and layers)
            attentions = outputs.attentions
            avg_attention = torch.stack(attentions).mean(dim=0).mean(dim=1).squeeze()
            
            # Get tokens
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
            
            # Calculate importance scores (average attention to [CLS] token)
            cls_attention = avg_attention[:, 0]  # Attention to [CLS] token
            importance_scores = cls_attention.tolist()
        
        # Remove special tokens and their scores
        filtered_tokens = []
        filtered_scores = []
        
        for token, score in zip(tokens, importance_scores):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                filtered_tokens.append(token)
                filtered_scores.append(score)
        
        result = {
            'text': text,
            'tokens': filtered_tokens,
            'importance_scores': filtered_scores,
            'method': 'Attention'
        }
        
        return result
    
    def predict_with_explanation(self, text: str, method: str = 'lime') -> Dict:
        """
        Predict with explanation.
        
        Args:
            text: Input text
            method: Explanation method ('lime' or 'attention')
            
        Returns:
            Dictionary with prediction and explanation
        """
        if method == 'lime':
            return self.explain_prediction_lime(text)
        elif method == 'attention':
            prediction = self.predict_single(text)
            attention_info = self.get_attention_weights(text)
            
            # Get top important words
            word_scores = list(zip(attention_info['tokens'], attention_info['importance_scores']))
            word_scores.sort(key=lambda x: abs(x[1]), reverse=True)
            
            result = {
                'text': text,
                'prediction': prediction,
                'explanation': {
                    'method': 'Attention',
                    'important_words': [word for word, _ in word_scores[:10]],
                    'word_weights': dict(word_scores[:10]),
                    'all_tokens': attention_info['tokens'],
                    'all_scores': attention_info['importance_scores']
                }
            }
            
            return result
        else:
            raise ValueError(f"Unknown explanation method: {method}")
    
    def save_explanation_report(self, text: str, output_path: str = None):
        """
        Save detailed explanation report to file.
        
        Args:
            text: Input text
            output_path: Path to save the report
        """
        if output_path is None:
            output_path = os.path.join(self.model_path, 'explanation_report.json')
        
        # Get both LIME and attention explanations
        lime_result = self.explain_prediction_lime(text)
        attention_result = self.predict_with_explanation(text, method='attention')
        
        report = {
            'text': text,
            'timestamp': str(torch.cuda.get_device_name() if torch.cuda.is_available() else 'CPU'),
            'lime_explanation': lime_result['explanation'],
            'attention_explanation': attention_result['explanation'],
            'prediction': lime_result['prediction']
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Explanation report saved to {output_path}")
    
    def get_model_info(self) -> Dict:
        """
        Get model information.
        
        Returns:
            Dictionary with model details
        """
        return {
            'model_path': self.model_path,
            'device': str(self.device),
            'model_type': 'DistilBERTForSequenceClassification',
            'num_labels': 2,
            'label_map': self.label_map,
            'max_length': 512
        }


def main():
    """Test the inference module."""
    print("Testing Fake News Detection Inference...")
    
    # Initialize predictor (will use the trained model)
    predictor = FakeNewsPredictor()
    
    # Test texts
    test_texts = [
        "Breaking: Scientists discover cure for all diseases overnight!",
        "Federal Reserve announces interest rate decision following economic meeting",
        "SHOCKING: Government hiding truth about aliens for 50 years!",
        "University study shows correlation between exercise and mental health"
    ]
    
    print("\nTesting predictions:")
    print("=" * 50)
    
    for text in test_texts:
        # Get prediction with LIME explanation
        result = predictor.predict_with_explanation(text, method='lime')
        
        print(f"\nText: {text}")
        print(f"Prediction: {result['prediction']['label']} (Confidence: {result['prediction']['confidence']})")
        print(f"Important words: {result['explanation']['important_words'][:5]}")
    
    # Save explanation report for first text
    predictor.save_explanation_report(test_texts[0])
    
    print(f"\nModel info: {predictor.get_model_info()}")


if __name__ == "__main__":
    main()
