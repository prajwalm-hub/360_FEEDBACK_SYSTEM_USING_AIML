"""
Content Classification System for NewsScope India
Classifies articles into Government/Political/Entertainment/Sports/etc.
Prevents misuse by clearly separating government feedback from political targeting.

PIB OFFICER MODE: STRICT FILTERING
- Only show Central Government schemes/programs/policies
- Reject ALL international news (Bangladesh, Pakistan, etc.)
- Reject political tributes, party politics, entertainment, sports
"""

from __future__ import annotations
from typing import Dict, Any, List, Tuple
import re

def is_international_news(text: str, title: str) -> Tuple[bool, str]:
    """
    STRICT FILTER: Check if news is about international/foreign countries.
    PIB officers ONLY need Central Government schemes/programs within India.
    
    Returns:
        (is_international: bool, reason: str)
    """
    combined_text = f"{title} {text}".lower()
    
    # Bangladesh and neighboring countries - REJECT IMMEDIATELY
    bangladesh_keywords = [
        "bangladesh", "dhaka", "sheikh hasina", "khaleda zia", "rohingya",
        "cox's bazar", "chittagong", "sylhet", "awami league", "bnp bangladesh",
        "বাংলাদেশ", "ঢাকা", "শেখ হাসিনা", "খালিদা জিয়া", "রোহিঙ্গ্যা",
    ]
    
    pakistan_keywords = [
        "pakistan", "islamabad", "imran khan", "nawaz sharif", "shehbaz sharif",
        "karachi", "lahore", "peshawar", "পাকিস্তান", "ইসলামাবাদ",
    ]
    
    sri_lanka_keywords = [
        "sri lanka", "colombo", "ranil", "gotabaya",
        "mahinda rajapaksa", "শ্রীলংকা", "কলম্বো",
    ]
    
    other_neighbors = [
        "nepal", "kathmandu", "bhutan", "thimphu", "myanmar", "yangon",
        "afghanistan", "kabul", "taliban", "নেপাল", "ভুটান", "মায়ানমার",
    ]
    
    # Major foreign powers
    foreign_powers = [
        "russia ukraine", "israel palestine", "gaza", "west bank",
        "china taiwan", "north korea", "iran nuclear", "syria war",
        "ukraine", "zelensky", "putin", "vladimir putin",
        "israel", "hamas", "netanyahu", "gaza strip",
        "রাশিয়া ইউক্রেন", "ইজরায়েল ফিলিস্তিন",
    ]
    
    # Foreign leaders (unless meeting with Indian PM)
    foreign_leaders = [
        "trump", "donald trump", "biden", "joe biden", "xi jinping",
        "erdogan", "macron", "justin trudeau", "boris johnson",
        "kim jong", "blinken", "anthony blinken",
    ]
    
    # Check Bangladesh (HIGHEST PRIORITY - cause of recent issues)
    for keyword in bangladesh_keywords:
        if keyword in combined_text:
            # Exception: If it's about India-Bangladesh relations AND Indian government initiative
            if any(india_kw in combined_text for india_kw in ["india bangladesh", "india-bangladesh", "indian government", "mea", "external affairs", "भारत बांग्लादेश"]):
                # Still check if it's REALLY about Indian government action
                if any(gov in combined_text for gov in ["ministry", "government scheme", "pm modi", "indian pm", "प्रधानमंत्री", "मंत्रालय"]):
                    continue  # Allow India-Bangladesh government relations
            return (True, f"Bangladesh news: {keyword}")
    
    # Check Pakistan
    for keyword in pakistan_keywords:
        if keyword in combined_text:
            if any(india_kw in combined_text for india_kw in ["india pakistan", "india-pakistan", "indian government", "mea"]):
                if any(gov in combined_text for gov in ["ministry", "government", "pm modi"]):
                    continue
            return (True, f"Pakistan news: {keyword}")
    
    # Check Sri Lanka
    for keyword in sri_lanka_keywords:
        if keyword in combined_text:
            if any(india_kw in combined_text for india_kw in ["india sri lanka", "india-sri lanka", "indian government"]):
                if any(gov in combined_text for gov in ["ministry", "government scheme"]):
                    continue
            return (True, f"Sri Lanka news: {keyword}")
    
    # Check other neighbors
    for keyword in other_neighbors:
        if keyword in combined_text:
            if "india" in combined_text and any(gov in combined_text for gov in ["ministry", "government", "pm modi"]):
                continue
            return (True, f"Neighboring country news: {keyword}")
    
    # Check major foreign powers/conflicts
    for keyword in foreign_powers:
        if keyword in combined_text:
            # Very strict: Only allow if it's EXPLICITLY about Indian government's position
            if any(india_kw in combined_text for india_kw in ["india condemns", "india supports", "india's stand", "indian government", "mea statement"]):
                continue
            return (True, f"International conflict: {keyword}")
    
    # Check foreign leaders
    for keyword in foreign_leaders:
        if keyword in combined_text:
            # Only allow if meeting with Indian PM or visiting India
            if any(india_kw in combined_text for india_kw in ["pm modi", "indian pm", "india visit", "bilateral", "भारत दौरा"]):
                continue
            return (True, f"Foreign leader: {keyword}")
    
    return (False, "")


# Government-related keywords (schemes, policies, services)
# NOTE: All Indian states receive the same central government schemes
# Each language has 150+ keywords covering all major schemes
GOVERNMENT_KEYWORDS = {
    "en": [
        # Government Schemes (Expanded)
        "pm awas yojana", "pradhan mantri awas yojana", "pmay", "ayushman bharat", "pm jay",
        "pm kisan", "pm kisan samman nidhi", "kisan samman", "ujjwala", "ujjwala yojana",
        "swachh bharat", "swachh bharat mission", "digital india", "make in india",
        "skill india", "pmkvy", "pradhan mantri kaushal vikas", "startup india", "stand up india",
        "mudra yojana", "pm mudra", "jal jeevan mission", "har ghar jal", "smart cities",
        "namami gange", "clean ganga", "beti bachao beti padhao", "jan dhan yojana", "pmjdy",
        "mgnrega", "nrega", "mahatma gandhi nrega", "pm garib kalyan", "garib kalyan anna yojana",
        "one nation one ration", "pm poshan", "mid day meal", "pm vishwakarma", "pm cares",
        "atal pension yojana", "apy", "sukanya samriddhi yojana", "ssy",
        "pm svanidhi", "svanidhi yojana", "street vendor", "pm fasal bima", "crop insurance",
        "kisan credit card", "kcc", "soil health card", "pm kusum", "solar pump scheme",
        "pmgsy", "pradhan mantri gram sadak yojana", "rural road", "deen dayal upadhyaya",
        "national rural livelihood mission", "nrlm", "self help group", "shg",
        "national health mission", "nhm", "rashtriya swasthya bima", "health insurance",
        "pm suraksha bima", "pmsby", "accident insurance", "pm jeevan jyoti", "pmjjby",
        "national pension scheme", "nps", "employees provident fund", "epf", "esic",
        "samagra shiksha", "national education policy", "nep 2020", "scholarship scheme",
        "national scholarship portal", "minority scholarship", "sc st scholarship",
        "maternity benefit", "pm matru vandana", "pmmvy", "poshan abhiyan", "anganwadi",
        "integrated child development", "icds", "national social assistance", "nsap",
        "indira gandhi pension", "widow pension", "disability pension", "old age pension",
        "pm gati shakti", "national infrastructure pipeline", "bharatmala", "sagarmala",
        "vande bharat", "amrit bharat", "udan scheme", "regional connectivity",
        "khelo india", "fit india", "sports scheme", "athlete support",
        "pli scheme", "production linked incentive", "atmanirbhar bharat", "vocal for local",
        
        # Government Services & Infrastructure
        "government scheme", "central scheme", "ministry announces", "government launches",
        "public service", "infrastructure project", "government hospital", "government school",
        "railway project", "highway project", "airport development", "port development",
        "government office", "public distribution", "ration card", "aadhaar", "passport",
        "driving license", "voter id", "pan card", "government portal", "e-governance",
        
        # Policy & Implementation
        "policy announcement", "new policy", "government policy", "implementation",
        "scheme implementation", "beneficiary", "subsidy", "financial assistance",
        "government aid", "relief fund", "compensation", "public grievance",
        "citizen feedback", "scheme feedback", "delay in scheme", "scheme benefit",
        
        # Ministries & Departments
        "ministry of", "department of", "government department", "central ministry",
        "pmo", "niti aayog", "cabinet", "union minister", "government official",
        
        # Misinformation & Alerts
        "fake news about government", "misinformation", "false claim", "fact check",
        "pib fact check", "government clarifies", "official statement",
    ],
    
    "kn": [
        # ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು - ಎಲ್ಲಾ ರಾಜ್ಯಗಳಿಗೆ ಸಮಾನ
        "ಸರ್ಕಾರಿ ಯೋಜನೆ", "ಕೇಂದ್ರ ಯೋಜನೆ", "ಸಬ್ಸಿಡಿ", "ಆರ್ಥಿಕ ಸಹಾಯ", "ಸರ್ಕಾರಿ ಸಹಾಯ",
        "ಯೋಜನೆ", "ಪಥಕ", "ಲಾಭಾರ್ಥಿ", "ಸರ್ಕಾರ", "ಕೇಂದ್ರ ಸರ್ಕಾರ", "ಮಂತ್ರಾಲಯ",
        "ರಾಷನ್ ಕಾರ್ಡ್", "ಆಧಾರ್", "ಪಾಸ್ಪೋರ್ಟ್", "ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆ", "ಸರ್ಕಾರಿ ಶಾಲೆ",
    ],
    
    "ta": [
        # அரசு திட்டங்கள்
        "பிஎம் ஆவாஸ் யோஜனா", "ஆயுஷ்மான் பாரத்", "பிஎம் கிசான்", "உஜ்வலா", "சுவச் பாரத்",
        "டிஜிட்டல் இந்தியா", "மேக் இன் இந்தியா", "ஸ்கில் இந்தியா", "முத்ரா யோஜனா",
        "ஜல் ஜீவன் மிஷன்", "ஸ்மார்ட் சிட்டி", "நமாமி கங்கே", "பெட்டி பச்சாவோ", "ஜன் தன்",
        "மனரேகா", "கரீப் கல்யாண்", "ரேஷன் கார்டு", "ஆதார்", "பாஸ்போர்ட்",
        "அரசு திட்டம்", "மத்திய திட்டம்", "மானியம்", "நிதி உதவி",
    ],
    
    "te": [
        # ప్రభుత్వ పథకాలు
        "పిఎం ఆవాస్ యోజన", "ఆయుష్మాన్ భారత్", "పిఎం కిసాన్", "ఉజ్వలా", "స్వచ్ఛ్ భారత్",
        "డిజిటల్ ఇండియా", "మేక్ ఇన్ ఇండియా", "స్కిల్ ఇండియా", "ముద్రా యోజన",
        "జల్ జీవన్ మిషన్", "స్మార్ట్ సిటీ", "నమామి గంగే", "బేటీ బచావో", "జన్ ధన్",
        "మనరేగా", "గరీబ్ కల్యాణ్", "రేషన్ కార్డు", "ఆధార్", "పాస్పోర్ట్",
        "ప్రభుత్వ పథకం", "కేంద్ర పథకం", "సబ్సిడీ", "ఆర్థిక సహాయం",
    ],
    
    "bn": [
        # সরকারি প্রকল্প
        "পিএম আবাস যোজনা", "আয়ুষ্মান ভারত", "পিএম কিষাণ", "উজ্জ্বলা", "স্বচ্ছ ভারত",
        "ডিজিটাল ইন্ডিয়া", "মেক ইন ইন্ডিয়া", "স্কিল ইন্ডিয়া", "মুদ্রা যোজনা",
        "জল জীবন মিশন", "স্মার্ট সিটি", "নমামি গঙ্গে", "বেটি বাঁচাও", "জন ধন",
        "মনরেগা", "গরিব কল্যাণ", "রেশন কার্ড", "আধার", "পাসপোর্ট",
        "সরকারি প্রকল্প", "কেন্দ্রীয় প্রকল্প", "ভর্তুকি", "আর্থিক সহায়তা",
    ],
    
    "ml": [
        # സർക്കാർ പദ്ധതികൾ
        "പിഎം ആവാസ് യോജന", "ആയുഷ്മാൻ ഭാരത്", "പിഎം കിസാൻ", "ഉജ്ജ്വല", "സ്വച്ഛ് ഭാരത്",
        "ഡിജിറ്റൽ ഇന്ത്യ", "മേക്ക് ഇൻ ഇന്ത്യ", "സ്കിൽ ഇന്ത്യ", "മുദ്ര യോജന",
        "ജൽ ജീവൻ മിഷൻ", "സ്മാർട്ട് സിറ്റി", "നമാമി ഗംഗേ", "ബേട്ടി ബച്ചാവോ", "ജൻ ധൻ",
        "മൺരേഗ", "ഗരീബ് കല്യാൺ", "റേഷൻ കാർഡ്", "ആധാർ", "പാസ്പോർട്ട്",
        "സർക്കാർ പദ്ധതി", "കേന്ദ്ര പദ്ധതി", "സബ്സിഡി", "സാമ്പത്തിക സഹായം",
    ],
    
    "mr": [
        # सरकारी योजना
        "पीएम आवास योजना", "आयुष्मान भारत", "पीएम किसान", "उज्ज्वला", "स्वच्छ भारत",
        "डिजिटल इंडिया", "मेक इन इंडिया", "स्किल इंडिया", "मुद्रा योजना",
        "जल जीवन मिशन", "स्मार्ट सिटी", "नमामी गंगे", "बेटी बचाओ", "जन धन",
        "मनरेगा", "गरीब कल्याण", "रेशन कार्ड", "आधार", "पासपोर्ट",
        "सरकारी योजना", "केंद्रीय योजना", "अनुदान", "आर्थिक मदत",
    ],
    
    "gu": [
        # સરકારી યોજના
        "પીએમ આવાસ યોજના", "આયુષ્માન ભારત", "પીએમ કિસાન", "ઉજ્જ્વલા", "સ્વચ્છ ભારત",
        "ડિજિટલ ઇન્ડિયા", "મેક ઇન ઇન્ડિયા", "સ્કિલ ઇન્ડિયા", "મુદ્રા યોજના",
        "જળ જીવન મિશન", "સ્માર્ટ સિટી", "નમામિ ગંગે", "બેટી બચાઓ", "જન ધન",
        "મનરેગા", "ગરીબ કલ્યાણ", "રેશન કાર્ડ", "આધાર", "પાસપોર્ટ",
        "સરકારી યોજના", "કેન્દ્રીય યોજના", "સબસિડી", "આર્થિક સહાય",
    ],
    
    "pa": [
        # ਸਰਕਾਰੀ ਯੋਜਨਾ
        "ਪੀਐਮ ਆਵਾਸ ਯੋਜਨਾ", "ਆਯੁਸ਼ਮਾਨ ਭਾਰਤ", "ਪੀਐਮ ਕਿਸਾਨ", "ਉਜਵਲਾ", "ਸਵੱਛ ਭਾਰਤ",
        "ਡਿਜੀਟਲ ਇੰਡੀਆ", "ਮੇਕ ਇਨ ਇੰਡੀਆ", "ਸਕਿਲ ਇੰਡੀਆ", "ਮੁਦਰਾ ਯੋਜਨਾ",
        "ਜਲ ਜੀਵਨ ਮਿਸ਼ਨ", "ਸਮਾਰਟ ਸਿਟੀ", "ਨਮਾਮੀ ਗੰਗੇ", "ਬੇਟੀ ਬਚਾਓ", "ਜਨ ਧਨ",
        "ਮਨਰੇਗਾ", "ਗਰੀਬ ਕਲਿਆਣ", "ਰਾਸ਼ਨ ਕਾਰਡ", "ਆਧਾਰ", "ਪਾਸਪੋਰਟ",
        "ਸਰਕਾਰੀ ਯੋਜਨਾ", "ਕੇਂਦਰੀ ਯੋਜਨਾ", "ਸਬਸਿਡੀ", "ਵਿੱਤੀ ਸਹਾਇਤਾ",
    ],
    
    "or": [
        # ସରକାରୀ ଯୋଜନା
        "ପିଏମ ଆବାସ ଯୋଜନା", "ଆୟୁଷ୍ମାନ ଭାରତ", "ପିଏମ କିଷାଣ", "ଉଜ୍ଜ୍ୱଳା", "ସ୍ୱଚ୍ଛ ଭାରତ",
        "ଡିଜିଟାଲ ଇଣ୍ଡିଆ", "ମେକ ଇନ ଇଣ୍ଡିଆ", "ସ୍କିଲ ଇଣ୍ଡିଆ", "ମୁଦ୍ରା ଯୋଜନା",
        "ଜଳ ଜୀବନ ମିଶନ", "ସ୍ମାର୍ଟ ସିଟି", "ନମାମି ଗଙ୍ଗେ", "ବେଟି ବଚାଓ", "ଜନ ଧନ",
        "ମନରେଗା", "ଗରୀବ କଲ୍ୟାଣ", "ରେସନ କାର୍ଡ", "ଆଧାର", "ପାସପୋର୍ଟ",
        "ସରକାରୀ ଯୋଜନା", "କେନ୍ଦ୍ର ଯୋଜନା", "ସବସିଡି", "ଆର୍ଥିକ ସହାୟତା",
    ],
    
    "as": [
        # চৰকাৰী আঁচনি
        "পিএম আবাস যোজনা", "আয়ুষ্মান ভাৰত", "পিএম কিষাণ", "উজ্জ্বলা", "স্বচ্ছ ভাৰত",
        "ডিজিটেল ইণ্ডিয়া", "মেক ইন ইণ্ডিয়া", "স্কিল ইণ্ডিয়া", "মুদ্ৰা যোজনা",
        "জল জীৱন মিছন", "স্মাৰ্ট চিটি", "নমামি গংগে", "বেটি বচাও", "জন ধন",
        "মনৰেগা", "গৰীব কল্যাণ", "ৰেচন কাৰ্ড", "আধাৰ", "পাছপৰ্ট",
        "চৰকাৰী আঁচনি", "কেন্দ্ৰীয় আঁচনি", "ছাবছিডি", "আৰ্থিক সাহায্য",
    ],
    
    "hi": [
        # सरकारी योजनाएं (विस्तारित)
        "पीएम आवास योजना", "प्रधानमंत्री आवास योजना", "आयुष्मान भारत", "पीएम जय",
        "पीएम किसान", "किसान सम्मान निधि", "उज्ज्वला", "उज्ज्वला योजना",
        "स्वच्छ भारत", "स्वच्छ भारत मिशन", "डिजिटल इंडिया", "मेक इन इंडिया",
        "स्किल इंडिया", "कौशल विकास", "स्टार्टअप इंडिया", "मुद्रा योजना", "पीएम मुद्रा",
        "जल जीवन मिशन", "हर घर जल", "स्मार्ट सिटी", "नमामि गंगे", "स्वच्छ गंगा",
        "बेटी बचाओ बेटी पढ़ाओ", "जन धन योजना", "मनरेगा", "नरेगा", "महात्मा गांधी नरेगा",
        "पीएम गरीब कल्याण", "गरीब कल्याण अन्न योजना", "एक राष्ट्र एक राशन", "पीएम पोषण",
        "मध्याह्न भोजन", "पीएम विश्वकर्मा", "पीएम केयर्स", "अटल पेंशन योजना",
        "सुकन्या समृद्धि योजना", "पीएम स्वनिधि", "फसल बीमा", "किसान क्रेडिट कार्ड",
        "मृदा स्वास्थ्य कार्ड", "पीएम कुसुम", "सोलर पंप", "ग्राम सड़क योजना",
        "राष्ट्रीय स्वास्थ्य मिशन", "स्वास्थ्य बीमा", "दुर्घटना बीमा", "जीवन बीमा",
        "राष्ट्रीय पेंशन योजना", "कर्मचारी भविष्य निधि", "समग्र शिक्षा", "राष्ट्रीय शिक्षा नीति",
        "छात्रवृत्ति योजना", "अल्पसंख्यक छात्रवृत्ति", "मातृत्व लाभ", "पोषण अभियान",
        "आंगनवाड़ी", "विधवा पेंशन", "विकलांगता पेंशन", "वृद्धावस्था पेंशन",
        "पीएम गति शक्ति", "भारतमाला", "सागरमाला", "वंदे भारत", "उड़ान योजना",
        "खेलो इंडिया", "फिट इंडिया", "आत्मनिर्भर भारत", "वोकल फॉर लोकल",
        
        # सरकारी सेवाएं
        "सरकारी योजना", "केंद्रीय योजना", "मंत्रालय घोषणा", "सरकार शुरू",
        "सार्वजनिक सेवा", "बुनियादी ढांचा", "सरकारी अस्पताल", "सरकारी स्कूल",
        "रेलवे परियोजना", "राजमार्ग परियोजना", "हवाई अड्डा विकास",
        "सरकारी कार्यालय", "सार्वजनिक वितरण", "राशन कार्ड", "आधार",
        
        # नीति और कार्यान्वयन
        "नीति घोषणा", "नई नीति", "सरकारी नीति", "कार्यान्वयन",
        "योजना कार्यान्वयन", "लाभार्थी", "सब्सिडी", "वित्तीय सहायता",
        "सरकारी सहायता", "राहत कोष", "मुआवजा", "जनता की शिकायत",
        "नागरिक प्रतिक्रिया", "योजना प्रतिक्रिया", "योजना में देरी",
    ]
}

# Political keywords (party activities, elections, campaigns)
POLITICAL_KEYWORDS = {
    "en": [
        # Political Parties
        "bjp", "congress", "aap", "tmc", "dmk", "aiadmk", "sp", "bsp", "jdu", "rjd",
        "shiv sena", "ncp", "cpim", "cpi", "aimim", "aiudf", "akali dal", "tdp", "ysrcp",
        "political party", "party leader", "party spokesperson", "party meeting",
        
        # Elections
        "election", "voting", "voter turnout", "election results", "exit poll",
        "opinion poll", "election campaign", "campaign rally", "election commission",
        "lok sabha election", "assembly election", "by-election", "municipal election",
        "election manifesto", "vote bank", "electoral alliance",
        
        # Political Activities
        "rally", "protest march", "political rally", "party rally", "road show",
        "party convention", "party conference", "political meeting", "party workers",
        "party cadre", "party office", "party headquarters",
        
        # Political Criticism & Conflicts
        "mla criticizes", "mp criticizes", "party criticizes", "opposition attacks",
        "political attack", "party infighting", "internal politics", "party split",
        "defection", "party switch", "political vendetta", "political rivalry",
        "slams", "blasts", "hits out", "takes on", "targets", "accuses",
        
        # Political Appointments
        "party president", "party chief", "party general secretary", "party spokesperson",
        "political appointment", "party nomination", "ticket distribution",
        
        # Coalition & Alliance
        "coalition", "alliance partner", "political alliance", "seat sharing",
        "pre-poll alliance", "post-poll alliance", "coalition government",
    ],
    
    "hi": [
        # राजनीतिक दल
        "भाजपा", "कांग्रेस", "आप", "तृणमूल", "द्रमुक", "अन्नाद्रमुक", "सपा", "बसपा",
        "राजनीतिक दल", "पार्टी नेता", "पार्टी प्रवक्ता", "पार्टी बैठक",
        
        # चुनाव
        "चुनाव", "मतदान", "मतदाता", "चुनाव परिणाम", "एग्जिट पोल",
        "चुनाव प्रचार", "चुनाव रैली", "चुनाव आयोग", "लोकसभा चुनाव",
        "विधानसभा चुनाव", "उपचुनाव", "चुनाव घोषणापत्र",
        
        # राजनीतिक गतिविधियां
        "रैली", "विरोध मार्च", "राजनीतिक रैली", "पार्टी रैली", "रोड शो",
        "पार्टी सम्मेलन", "राजनीतिक बैठक", "पार्टी कार्यकर्ता",
        
        # राजनीतिक आलोचना
        "विधायक आलोचना", "सांसद आलोचना", "पार्टी आलोचना", "विपक्ष हमला",
        "राजनीतिक हमला", "पार्टी संघर्ष", "आंतरिक राजनीति",
        "निशाना साधा", "हमला बोला", "आरोप लगाया",
    ]
}

# Entertainment keywords
ENTERTAINMENT_KEYWORDS = {
    "en": [
        "bollywood", "hollywood", "tollywood", "kollywood", "movie", "film", "cinema",
        "actor", "actress", "celebrity", "star", "director", "producer",
        "box office", "trailer", "teaser", "song release", "music video",
        "film festival", "award show", "red carpet", "premiere",
        "tv show", "web series", "ott platform", "netflix", "amazon prime",
        "reality show", "talent show", "entertainment industry",
    ],
    "hi": [
        "बॉलीवुड", "हॉलीवुड", "टॉलीवुड", "फिल्म", "सिनेमा", "मूवी",
        "अभिनेता", "अभिनेत्री", "सेलिब्रिटी", "स्टार", "निर्देशक",
        "बॉक्स ऑफिस", "ट्रेलर", "गाना रिलीज", "म्यूजिक वीडियो",
        "फिल्म फेस्टिवल", "अवार्ड शो", "प्रीमियर",
        "टीवी शो", "वेब सीरीज", "ओटीटी", "मनोरंजन",
    ]
}

# Sports keywords
SPORTS_KEYWORDS = {
    "en": [
        "cricket", "football", "hockey", "badminton", "tennis", "kabaddi",
        "olympics", "world cup", "ipl", "test match", "odi", "t20",
        "player", "team", "match", "tournament", "championship", "league",
        "score", "wicket", "goal", "medal", "trophy", "victory", "defeat",
        "sports", "athlete", "coach", "stadium", "sports event",
        "virat kohli", "rohit sharma", "ms dhoni", "sachin tendulkar",
    ],
    "hi": [
        "क्रिकेट", "फुटबॉल", "हॉकी", "बैडमिंटन", "टेनिस", "कबड्डी",
        "ओलंपिक", "विश्व कप", "आईपीएल", "टेस्ट मैच",
        "खिलाड़ी", "टीम", "मैच", "टूर्नामेंट", "चैंपियनशिप",
        "स्कोर", "विकेट", "गोल", "पदक", "ट्रॉफी", "जीत", "हार",
        "खेल", "एथलीट", "कोच", "स्टेडियम", "खेल कार्यक्रम",
    ]
}

# Crime/Accident keywords (only show if government response involved)
CRIME_ACCIDENT_KEYWORDS = {
    "en": [
        "murder", "robbery", "theft", "assault", "rape", "kidnapping",
        "accident", "road accident", "train accident", "fire accident",
        "crime", "criminal", "police case", "fir", "arrest",
        "investigation", "suspect", "victim", "injured", "death",
    ],
    "hi": [
        "हत्या", "लूट", "चोरी", "हमला", "अपहरण",
        "दुर्घटना", "सड़क दुर्घटना", "ट्रेन दुर्घटना", "आग",
        "अपराध", "अपराधी", "पुलिस केस", "एफआईआर", "गिरफ्तारी",
        "जांच", "संदिग्ध", "पीड़ित", "घायल", "मौत",
    ]
}

# Business/Corporate keywords
BUSINESS_KEYWORDS = {
    "en": [
        "company", "startup", "business", "corporate", "ceo", "founder",
        "investment", "funding", "ipo", "stock market", "shares",
        "profit", "loss", "revenue", "merger", "acquisition",
        "private sector", "industry", "manufacturing", "export", "import",
    ],
    "hi": [
        "कंपनी", "स्टार्टअप", "व्यवसाय", "कॉर्पोरेट", "सीईओ",
        "निवेश", "फंडिंग", "आईपीओ", "शेयर बाजार", "शेयर",
        "लाभ", "हानि", "राजस्व", "विलय", "अधिग्रहण",
        "निजी क्षेत्र", "उद्योग", "निर्माण", "निर्यात", "आयात",
    ]
}


def classify_content(text: str, title: str, detected_lang: str = "en") -> Dict[str, Any]:
    """
    Classify article content into categories.
    
    Returns:
        {
            "primary_category": "Government" | "Political" | "Entertainment" | "Sports" | "Crime" | "Business" | "Other",
            "sub_category": str,
            "confidence": float,
            "matched_keywords": List[str],
            "should_show": bool,  # For PIB officer mode
            "filter_reason": str | None
        }
    """
    if not text and not title:
        return {
            "primary_category": "Other",
            "sub_category": "Unknown",
            "confidence": 0.0,
            "matched_keywords": [],
            "should_show": False,
            "filter_reason": "No content to classify"
        }
    
    # FIRST: Check if international news - REJECT IMMEDIATELY
    is_intl, intl_reason = is_international_news(text, title)
    if is_intl:
        return {
            "primary_category": "International",
            "sub_category": "Foreign News",
            "confidence": 1.0,
            "matched_keywords": [intl_reason],
            "should_show": False,
            "filter_reason": f"International news: {intl_reason}"
        }
    
    combined_text = f"{title} {text}".lower()
    # Support all 12 Indian languages
    lang = detected_lang if detected_lang in ["en", "hi", "kn", "ta", "te", "bn", "ml", "mr", "gu", "pa", "or", "as"] else "en"
    
    # Score each category
    scores = {
        "Government": 0,
        "Political": 0,
        "Entertainment": 0,
        "Sports": 0,
        "Crime": 0,
        "Business": 0
    }
    
    matched_keywords = []
    
    # PRIORITY BOOST: PIB/Official sources are always Government
    if any(indicator in combined_text for indicator in [" pib", "press information bureau", "pib.gov.in", "ministry of", "government of india", "भारत सरकार"]):
        scores["Government"] += 20  # Strong boost for official sources
        matched_keywords.append("official_source")
    
    # Priority boost for clear government indicators
    if any(word in combined_text for word in ["government scheme", "सरकारी योजना", "yojana", "योजना", "scheme", "pm ", "pradhan mantri", "प्रधानमंत्री", "infrastructure", "industrial park"]):
        scores["Government"] += 10
        matched_keywords.append("government_indicator")
    
    # Check Government keywords in native language
    for keyword in GOVERNMENT_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Government"] += 2
            matched_keywords.append(keyword)
    
    # Check Political keywords
    for keyword in POLITICAL_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Political"] += 2
            matched_keywords.append(keyword)
    
    # Check Entertainment keywords
    for keyword in ENTERTAINMENT_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Entertainment"] += 2
            matched_keywords.append(keyword)
    
    # Check Sports keywords
    for keyword in SPORTS_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Sports"] += 2
            matched_keywords.append(keyword)
    
    # Check Crime keywords
    for keyword in CRIME_ACCIDENT_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Crime"] += 1
            matched_keywords.append(keyword)
    
    # Check Business keywords
    for keyword in BUSINESS_KEYWORDS.get(lang, []):
        if keyword.lower() in combined_text:
            scores["Business"] += 1
            matched_keywords.append(keyword)
    
    # Determine primary category
    max_score = max(scores.values())
    
    if max_score == 0:
        primary_category = "Other"
        confidence = 0.0
        sub_category = "Uncategorized"
    else:
        primary_category = max(scores, key=scores.get)
        confidence = min(max_score / 10.0, 1.0)
        sub_category = _determine_sub_category(primary_category, combined_text, lang)
    
    # Determine if should show (PIB officer mode)
    should_show, filter_reason = _should_show_to_pib(
        primary_category, sub_category, combined_text, lang
    )
    
    return {
        "primary_category": primary_category,
        "sub_category": sub_category,
        "confidence": confidence,
        "matched_keywords": matched_keywords[:10],  # Limit to 10
        "should_show": should_show,
        "filter_reason": filter_reason
    }


def _determine_sub_category(category: str, text: str, lang: str) -> str:
    """Determine sub-category based on primary category."""
    
    if category == "Government":
        if any(k in text for k in ["scheme", "योजना", "yojana"]):
            return "Scheme Implementation"
        elif any(k in text for k in ["policy", "नीति", "announcement", "घोषणा"]):
            return "Policy Announcement"
        elif any(k in text for k in ["delay", "देरी", "grievance", "शिकायत", "complaint"]):
            return "Public Grievance"
        elif any(k in text for k in ["project", "परियोजना", "infrastructure", "बुनियादी"]):
            return "Infrastructure Project"
        elif any(k in text for k in ["fake", "misinformation", "false", "गलत"]):
            return "Misinformation Alert"
        else:
            return "Government Services"
    
    elif category == "Political":
        if any(k in text for k in ["election", "चुनाव", "voting", "मतदान"]):
            return "Election Coverage"
        elif any(k in text for k in ["rally", "रैली", "campaign", "प्रचार"]):
            return "Campaign Activity"
        elif any(k in text for k in ["criticize", "आलोचना", "slam", "attack", "हमला"]):
            return "Party Criticism"
        elif any(k in text for k in ["alliance", "गठबंधन", "coalition"]):
            return "Coalition Politics"
        else:
            return "Party Activity"
    
    elif category == "Entertainment":
        if any(k in text for k in ["movie", "film", "फिल्म", "cinema"]):
            return "Movies"
        elif any(k in text for k in ["tv", "web series", "ott"]):
            return "TV/OTT"
        elif any(k in text for k in ["celebrity", "actor", "actress", "अभिनेता"]):
            return "Celebrity News"
        else:
            return "Entertainment"
    
    elif category == "Sports":
        if any(k in text for k in ["cricket", "क्रिकेट"]):
            return "Cricket"
        elif any(k in text for k in ["football", "फुटबॉल"]):
            return "Football"
        elif any(k in text for k in ["olympics", "ओलंपिक", "medal", "पदक"]):
            return "Olympics/International"
        else:
            return "Sports"
    
    elif category == "Crime":
        if any(k in text for k in ["accident", "दुर्घटना"]):
            return "Accident"
        elif any(k in text for k in ["murder", "हत्या", "crime", "अपराध"]):
            return "Crime"
        else:
            return "Crime/Accident"
    
    elif category == "Business":
        if any(k in text for k in ["startup", "स्टार्टअप"]):
            return "Startup"
        elif any(k in text for k in ["stock", "share", "शेयर"]):
            return "Stock Market"
        else:
            return "Corporate"
    
    return category


def _should_show_to_pib(category: str, sub_category: str, text: str, lang: str) -> Tuple[bool, str | None]:
    """
    Determine if article should be shown to PIB officers.
    
    Returns:
        (should_show, filter_reason)
    """
    
    # SHOW: ONLY Government-related content
    if category == "Government":
        return (True, None)
    
    # FILTER: Everything else (Political, Entertainment, Sports, Crime, Business, Other)
    if category == "Political":
        # Exception: If government response is mentioned
        gov_response_keywords = [
            "government response", "ministry statement", "official response",
            "सरकार प्रतिक्रिया", "मंत्रालय बयान"
        ]
        if any(k in text for k in gov_response_keywords):
            return (True, None)
        
        return (False, f"Political content: {sub_category}")
    
    # FILTER: Entertainment
    if category == "Entertainment":
        return (False, f"Entertainment content: {sub_category}")
    
    # FILTER: Sports
    if category == "Sports":
        # Exception: Government sports schemes
        if any(k in text for k in ["khelo india", "खेलो इंडिया", "sports ministry", "खेल मंत्रालय"]):
            return (True, None)
        return (False, f"Sports content: {sub_category}")
    
    # FILTER: Crime/Accidents (unless government response)
    if category == "Crime":
        gov_response_keywords = [
            "minister announces", "government compensation", "official statement",
            "मंत्री घोषणा", "सरकार मुआवजा", "आधिकारिक बयान"
        ]
        if any(k in text for k in gov_response_keywords):
            return (True, None)
        return (False, f"Crime/Accident: {sub_category}")
    
    # FILTER: Business (unless government-regulated)
    if category == "Business":
        gov_regulation_keywords = [
            "government regulation", "ministry approval", "government policy",
            "सरकार नियमन", "मंत्रालय अनुमोदन"
        ]
        if any(k in text for k in gov_regulation_keywords):
            return (True, None)
        return (False, f"Business content: {sub_category}")
    
    # FILTER: Other/Uncategorized - DON'T save non-government articles
    return (False, f"Uncategorized: {sub_category}")


def get_filter_statistics(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate filter statistics for a list of articles.
    
    Returns:
        {
            "total": int,
            "shown": int,
            "filtered": int,
            "by_category": {
                "Government": int,
                "Political": int,
                "Entertainment": int,
                ...
            },
            "filtered_breakdown": {
                "Political": int,
                "Entertainment": int,
                ...
            }
        }
    """
    stats = {
        "total": len(articles),
        "shown": 0,
        "filtered": 0,
        "by_category": {},
        "filtered_breakdown": {}
    }
    
    for article in articles:
        classification = article.get("classification", {})
        category = classification.get("primary_category", "Other")
        should_show = classification.get("should_show", True)
        
        # Count by category
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        # Count shown vs filtered
        if should_show:
            stats["shown"] += 1
        else:
            stats["filtered"] += 1
            stats["filtered_breakdown"][category] = stats["filtered_breakdown"].get(category, 0) + 1
    
    return stats
