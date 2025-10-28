"""
Text analysis pipeline using Hugging Face models.
"""
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
import spacy

# Configure logging
logger = logging.getLogger(__name__)

# Global variables to store loaded models
nlp_fr = None
sentiment_pipeline = None
summarization_pipeline = None
keyword_model = None

def load_models():
    """
    Load all text analysis models.
    This function should be called once during application startup.
    """
    global nlp_fr, sentiment_pipeline, summarization_pipeline, keyword_model
    
    logger.info("Loading text analysis models...")
    
    try:
        # French NLP model for topic extraction
        nlp_fr = spacy.load("fr_core_news_md")
        logger.info("French NLP model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load French NLP model: {e}")
    
    try:
        # Sentiment analysis model
        sentiment_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
        sentiment_model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-xlm-roberta-base-sentiment")
        sentiment_pipeline = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)
        logger.info("Sentiment analysis model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load sentiment analysis model: {e}")
    
    try:
        # Summarization model
        summarization_tokenizer = AutoTokenizer.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
        summarization_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
        summarization_pipeline = pipeline("summarization", model=summarization_model, tokenizer=summarization_tokenizer)
        logger.info("Summarization model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load summarization model: {e}")
    
    try:
        # Keyword extraction model
        sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        keyword_model = KeyBERT(model=sentence_model)
        logger.info("Keyword extraction model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load keyword extraction model: {e}")


def analyze_sentiment(text):
    """
    Analyze the sentiment of a text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: A dictionary containing the sentiment label and score
    """
    if not text or not sentiment_pipeline:
        return {"sentiment": "neutre", "emotion_score": 0.5}
    
    try:
        result = sentiment_pipeline(text)[0]
        
        # Map the model's output to our expected format
        label_mapping = {
            "LABEL_0": "negatif",
            "LABEL_1": "neutre",
            "LABEL_2": "positif"
        }
        
        sentiment = label_mapping.get(result["label"], "neutre")
        score = result["score"]
        
        return {
            "sentiment": sentiment,
            "emotion_score": score
        }
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        return {"sentiment": "neutre", "emotion_score": 0.5}


def extract_keywords(text, top_n=5):
    """
    Extract keywords from a text.
    
    Args:
        text (str): The text to analyze
        top_n (int): The number of keywords to extract
        
    Returns:
        list: A list of keywords
    """
    if not text or not keyword_model:
        return []
    
    try:
        # Extract keywords
        keywords = keyword_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='french', 
            top_n=top_n
        )
        
        # Return only the keywords, not the scores
        return [keyword for keyword, _ in keywords]
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []


def extract_topics(text, top_n=3):
    """
    Extract topics from a text using NLP.
    
    Args:
        text (str): The text to analyze
        top_n (int): The number of topics to extract
        
    Returns:
        list: A list of topics
    """
    if not text or not nlp_fr:
        return []
    
    try:
        # Process the text with spaCy
        doc = nlp_fr(text)
        
        # Extract noun phrases as potential topics
        noun_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 2:  # Limit to 1-2 word phrases
                noun_phrases.append(chunk.text.lower())
        
        # Get unique topics
        topics = list(set(noun_phrases))
        
        # Limit to top_n topics
        return topics[:top_n]
    except Exception as e:
        logger.error(f"Error extracting topics: {e}")
        return []


def generate_summary(text, max_length=150):
    """
    Generate a summary of a text.
    
    Args:
        text (str): The text to summarize
        max_length (int): The maximum length of the summary
        
    Returns:
        str: The summary
    """
    if not text or not summarization_pipeline or len(text.split()) < 30:
        return text[:max_length] if text else ""
    
    try:
        # Set language for mbart model
        summarization_pipeline.tokenizer.src_lang = "fr_XX"
        
        # Generate summary
        summary = summarization_pipeline(
            text,
            max_length=max_length,
            min_length=30,
            do_sample=False
        )[0]["summary_text"]
        
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return text[:max_length] if text else ""

