"""
NLP-based Geographic Classification Module
Detects location entities and maps them to Indian states
"""
import logging
from typing import Optional, Dict, List, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

logger = logging.getLogger(__name__)

# City to State mapping for major Indian cities
CITY_STATE_MAP = {
    # Karnataka
    "bangalore": "Karnataka", "bengaluru": "Karnataka", "mysore": "Karnataka", "mysuru": "Karnataka",
    "mangalore": "Karnataka", "hubli": "Karnataka", "belgaum": "Karnataka", "davangere": "Karnataka",
    
    # Maharashtra
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra", "thane": "Maharashtra",
    "nashik": "Maharashtra", "aurangabad": "Maharashtra", "solapur": "Maharashtra", "kolhapur": "Maharashtra",
    
    # Tamil Nadu
    "chennai": "Tamil Nadu", "coimbatore": "Tamil Nadu", "madurai": "Tamil Nadu", "tiruchirappalli": "Tamil Nadu",
    "salem": "Tamil Nadu", "tirunelveli": "Tamil Nadu", "vellore": "Tamil Nadu", "erode": "Tamil Nadu",
    
    # Delhi
    "delhi": "Delhi", "new delhi": "Delhi", "newdelhi": "Delhi",
    
    # West Bengal
    "kolkata": "West Bengal", "calcutta": "West Bengal", "howrah": "West Bengal", "durgapur": "West Bengal",
    "asansol": "West Bengal", "siliguri": "West Bengal",
    
    # Gujarat
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat", "rajkot": "Gujarat",
    "bhavnagar": "Gujarat", "jamnagar": "Gujarat", "gandhinagar": "Gujarat",
    
    # Rajasthan
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan", "kota": "Rajasthan",
    "ajmer": "Rajasthan", "bikaner": "Rajasthan",
    
    # Uttar Pradesh
    "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh", "agra": "Uttar Pradesh", "varanasi": "Uttar Pradesh",
    "meerut": "Uttar Pradesh", "allahabad": "Uttar Pradesh", "prayagraj": "Uttar Pradesh", "noida": "Uttar Pradesh",
    "ghaziabad": "Uttar Pradesh", "bareilly": "Uttar Pradesh",
    
    # Madhya Pradesh
    "bhopal": "Madhya Pradesh", "indore": "Madhya Pradesh", "gwalior": "Madhya Pradesh", "jabalpur": "Madhya Pradesh",
    "ujjain": "Madhya Pradesh",
    
    # Bihar
    "patna": "Bihar", "gaya": "Bihar", "bhagalpur": "Bihar", "muzaffarpur": "Bihar",
    
    # Telangana
    "hyderabad": "Telangana", "warangal": "Telangana", "nizamabad": "Telangana",
    
    # Andhra Pradesh
    "visakhapatnam": "Andhra Pradesh", "vijayawada": "Andhra Pradesh", "guntur": "Andhra Pradesh",
    "tirupati": "Andhra Pradesh", "amaravati": "Andhra Pradesh",
    
    # Kerala
    "thiruvananthapuram": "Kerala", "kochi": "Kerala", "cochin": "Kerala", "kozhikode": "Kerala",
    "calicut": "Kerala", "thrissur": "Kerala", "kollam": "Kerala",
    
    # Odisha
    "bhubaneswar": "Odisha", "cuttack": "Odisha", "rourkela": "Odisha",
    
    # Punjab
    "chandigarh": "Punjab", "ludhiana": "Punjab", "amritsar": "Punjab", "jalandhar": "Punjab",
    
    # Haryana
    "faridabad": "Haryana", "gurugram": "Haryana", "gurgaon": "Haryana", "panipat": "Haryana",
    
    # Jharkhand
    "ranchi": "Jharkhand", "jamshedpur": "Jharkhand", "dhanbad": "Jharkhand",
    
    # Assam
    "guwahati": "Assam", "dispur": "Assam", "silchar": "Assam",
    
    # Uttarakhand
    "dehradun": "Uttarakhand", "haridwar": "Uttarakhand", "rishikesh": "Uttarakhand",
    
    # Himachal Pradesh
    "shimla": "Himachal Pradesh", "dharamshala": "Himachal Pradesh", "manali": "Himachal Pradesh",
    
    # Jammu and Kashmir
    "srinagar": "Jammu and Kashmir", "jammu": "Jammu and Kashmir",
    
    # Goa
    "panaji": "Goa", "margao": "Goa", "vasco": "Goa",
    
    # Chhattisgarh
    "raipur": "Chhattisgarh", "bhilai": "Chhattisgarh",
    
    # Tripura
    "agartala": "Tripura",
    
    # Meghalaya
    "shillong": "Meghalaya",
    
    # Manipur
    "imphal": "Manipur",
    
    # Nagaland
    "kohima": "Nagaland",
    
    # Arunachal Pradesh
    "itanagar": "Arunachal Pradesh",
    
    # Mizoram
    "aizawl": "Mizoram",
    
    # Sikkim
    "gangtok": "Sikkim",
    
    # Puducherry
    "puducherry": "Puducherry", "pondicherry": "Puducherry",
}

# State name variations
STATE_VARIATIONS = {
    "karnataka": "Karnataka", "karnātaka": "Karnataka",
    "maharashtra": "Maharashtra", "mahārāshtra": "Maharashtra",
    "tamil nadu": "Tamil Nadu", "tamilnadu": "Tamil Nadu",
    "delhi": "Delhi",
    "west bengal": "West Bengal", "westbengal": "West Bengal",
    "gujarat": "Gujarat", "gujarāt": "Gujarat",
    "rajasthan": "Rajasthan", "rājasthān": "Rajasthan",
    "uttar pradesh": "Uttar Pradesh", "uttarpradesh": "Uttar Pradesh",
    "madhya pradesh": "Madhya Pradesh", "madhyapradesh": "Madhya Pradesh",
    "bihar": "Bihar", "bihār": "Bihar",
    "telangana": "Telangana", "telangāna": "Telangana",
    "andhra pradesh": "Andhra Pradesh", "andhrapradesh": "Andhra Pradesh",
    "kerala": "Kerala", "kēraḷa": "Kerala",
    "odisha": "Odisha", "orissa": "Odisha",
    "punjab": "Punjab", "panjāb": "Punjab",
    "haryana": "Haryana", "haryāṇā": "Haryana",
    "jharkhand": "Jharkhand", "jhārkhaṇḍ": "Jharkhand",
    "assam": "Assam", "āsām": "Assam",
}


class GeoClassifier:
    def __init__(self, use_ner: bool = True):
        self.use_ner = use_ner
        self.ner_pipeline = None
        
        if use_ner:
            try:
                model_name = "Davlan/xlm-roberta-base-ner-hrl"
                self.ner_pipeline = pipeline("ner", model=model_name, aggregation_strategy="simple")
                logger.info(f"[GEO] NER model loaded: {model_name}")
            except Exception as e:
                logger.warning(f"[GEO] NER model failed to load: {e}. Using keyword matching only.")
                self.use_ner = False
    
    def extract_locations_ner(self, text: str) -> List[Tuple[str, int]]:
        """Extract location entities using NER model"""
        if not self.ner_pipeline or not text:
            return []
        
        try:
            entities = self.ner_pipeline(text[:512])  # Limit text length
            locations = []
            
            for entity in entities:
                if entity['entity_group'] in ['LOC', 'GPE', 'LOCATION']:
                    location = entity['word'].strip().lower()
                    position = entity['start']
                    locations.append((location, position))
            
            return locations
        except Exception as e:
            logger.error(f"[GEO] NER extraction failed: {e}")
            return []
    
    def extract_locations_keyword(self, text: str) -> List[Tuple[str, int]]:
        """Extract locations using keyword matching"""
        if not text:
            return []
        
        text_lower = text.lower()
        locations = []
        
        # Check for cities
        for city, state in CITY_STATE_MAP.items():
            pos = text_lower.find(city)
            if pos != -1:
                locations.append((city, pos))
        
        # Check for states
        for state_var, state in STATE_VARIATIONS.items():
            pos = text_lower.find(state_var)
            if pos != -1:
                locations.append((state_var, pos))
        
        return locations
    
    def map_to_state(self, location: str) -> Optional[str]:
        """Map location to state"""
        location_lower = location.lower().strip()
        
        # Direct city match
        if location_lower in CITY_STATE_MAP:
            return CITY_STATE_MAP[location_lower]
        
        # State name match
        if location_lower in STATE_VARIATIONS:
            return STATE_VARIATIONS[location_lower]
        
        # Partial match for cities
        for city, state in CITY_STATE_MAP.items():
            if city in location_lower or location_lower in city:
                return state
        
        return None
    
    def classify(self, text: str, title: str = "") -> Optional[str]:
        """
        Classify article to a state based on location entities
        Returns state name or None
        """
        if not text and not title:
            return None
        
        # Combine title and text, prioritize title
        combined_text = f"{title} {text}" if title else text
        
        # Extract locations using both methods
        locations = []
        
        if self.use_ner:
            locations.extend(self.extract_locations_ner(combined_text))
        
        locations.extend(self.extract_locations_keyword(combined_text))
        
        if not locations:
            return None
        
        # Sort by position (earliest first)
        locations.sort(key=lambda x: x[1])
        
        # Try to map each location to a state
        for location, position in locations:
            state = self.map_to_state(location)
            if state:
                logger.info(f"[GEO] Detected: '{location}' → {state} (pos: {position})")
                return state
        
        return None


# Global instance
_geo_classifier = None

def get_geo_classifier() -> GeoClassifier:
    """Get or create global geo classifier instance"""
    global _geo_classifier
    if _geo_classifier is None:
        _geo_classifier = GeoClassifier(use_ner=False)  # Start with keyword only
    return _geo_classifier


def classify_article_region(article_dict: Dict) -> Optional[str]:
    """
    Classify article region based on content
    Returns state name or None
    """
    classifier = get_geo_classifier()
    
    title = article_dict.get('title', '')
    content = article_dict.get('content', '')
    summary = article_dict.get('summary', '')
    
    # Try title first (most relevant)
    state = classifier.classify(title)
    if state:
        return state
    
    # Try summary
    state = classifier.classify(summary)
    if state:
        return state
    
    # Try content (first 1000 chars)
    if content:
        state = classifier.classify(content[:1000])
        if state:
            return state
    
    return None
