"""
Central Government Schemes Database
This file contains all Central Government schemes, programs, and initiatives
for filtering PIB-related news and providing context to the AI assistant.
"""
from functools import lru_cache

CENTRAL_SCHEMES = [
    {
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Farmer welfare scheme providing income support to all landholding farmers",
        "tags": ["Agricultural Inputs", "Agriculture", "Farmers", "Income Support", "Kisan"],
        "regional_names": {
            "hi": ["पीएम किसान", "प्रधानमंत्री किसान सम्मान निधि", "किसान सम्मान निधि"],
            "kn": ["ಪಿಎಂ ಕಿಸಾನ್", "ಪ್ರಧಾನಮಂತ್ರಿ ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ"],
            "ta": ["பிஎம் கிசான்", "பிரதமர் கிசான் சம்மான் நிதி"],
            "te": ["పిఎమ్ కిసాన్", "ప్రధానమంత్రి కిసాన్ సమ్మాన్ నిధి"],
            "mr": ["पीएम किसान", "प्रधानमंत्री किसान सन्मान निधी"],
            "gu": ["પીએમ કિસાન", "પ્રધાનમંત્રી કિસાન સન્માન નિધિ"],
            "bn": ["পিএম কিষাণ", "প্রধানমন্ত্রী কিষাণ সম্মান নিধি"],
            "pa": ["ਪੀਐਮ ਕਿਸਾਨ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਕਿਸਾਨ ਸਮਾਨ ਨਿਧੀ"],
            "ml": ["പിഎം കിസാൻ", "പ്രധാനമന്ത്രി കിസാൻ സമ്മാൻ നിധി"],
            "or": ["ପିଏମ୍ କିସାନ", "ପ୍ରଧାନମନ୍ତ୍ରୀ କିସାନ ସମ୍ମାନ ନିଧି"],
            "as": ["পিএম কিষাণ", "প্ৰধানমন্ত্ৰী কিষাণ সন্মান নিধি"]
        }
    },
    {
        "name": "Ayushman Bharat - PM-JAY",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Health insurance scheme providing ₹5,00,000/- per family per year for secondary and tertiary care hospitalization",
        "tags": ["Health", "Insurance"],
        "regional_names": {
            "hi": ["आयुष्मान भारत", "पीएम जय", "आयुष्मान योजना"],
            "kn": ["ಆಯುಷ್ಮಾನ್ ಭಾರತ್", "ಪಿಎಂ ಜೆಎವೈ"],
            "ta": ["ஆயுஷ்மான் பாரத்", "பிஎம் ஜே"],
            "te": ["ఆయుష్మాన్ భారత్", "పిఎమ్ జేఏవై"],
            "mr": ["आयुष्मान भारत", "पीएम जय"],
            "gu": ["આયુષ્માન ભારત", "પીએમ જય"],
            "bn": ["আয়ুষ্মান ভারত", "পিএম জে"],
            "pa": ["ਆਯੁਸ਼ਮਾਨ ਭਾਰਤ", "ਪੀਐਮ ਜੇ"],
            "ml": ["ആയുഷ്മാൻ ഭാരത്", "പിഎം ജെ"],
            "or": ["ଆୟୁଷ୍ମାନ ଭାରତ", "ପିଏମ୍ ଜେ"],
            "as": ["আয়ুষ্মান ভাৰত", "পিএম জে"]
        }
    },
    {
        "name": "Pradhan Mantri Ujjwala Yojana",
        "ministry": "Ministry Of Petroleum and Natural Gas",
        "description": "LPG connections to women from Below Poverty Line (BPL) households",
        "tags": ["LPG", "Women Empowerment", "BPL"],
        "regional_names": {
            "hi": ["उज्ज्वला योजना", "प्रधानमंत्री उज्ज्वला योजना", "उज्ज्वला"],
            "kn": ["ಉಜ್ವಲಾ ಯೋಜನೆ", "ಪ್ರಧಾನಮಂತ್ರಿ ಉಜ್ವಲಾ"],
            "ta": ["உஜ்வலா திட்டம்", "பிரதமர் உஜ்வலா"],
            "te": ["ఉజ్వలా యోజన", "ప్రధానమంత్రి ఉజ్వలా"],
            "mr": ["उज्ज्वला योजना", "प्रधानमंत्री उज्ज्वला"],
            "gu": ["ઉજ્જવલા યોજના", "પ્રધાનમંત્રી ઉજ્જવલા"],
            "bn": ["উজ্জ্বলা যোজনা", "প্রধানমন্ত্রী উজ্জ্বলা"],
            "pa": ["ਉੱਜਵਲਾ ਯੋਜਨਾ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਉੱਜਵਲਾ"],
            "ml": ["ഉജ്വല യോജന", "പ്രധാനമന്ത്രി ഉജ്വല"],
            "or": ["ଉଜ୍ଜ୍ୱଳା ଯୋଜନା", "ପ୍ରଧାନମନ୍ତ୍ରୀ ଉଜ୍ଜ୍ୱଳା"],
            "as": ["উজ্জ্বলা যোজনা", "প্ৰধানমন্ত্ৰী উজ্জ্বলা"]
        }
    },
    {
        "name": "Pradhan Mantri Awas Yojana (PMAY)",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Housing for All scheme providing affordable housing to urban and rural poor",
        "tags": ["Housing", "Urban Development", "Rural Development"],
        "regional_names": {
            "hi": ["प्रधानमंत्री आवास योजना", "पीएम आवास", "आवास योजना"],
            "kn": ["ಪ್ರಧಾನಮಂತ್ರಿ ಆವಾಸ್ ಯೋಜನೆ", "ಪಿಎಂ ಆವಾಸ್"],
            "ta": ["பிரதமர் ஆவாஸ் திட்டம்", "பிஎம் ஆவாஸ்"],
            "te": ["ప్రధానమంత్రి ఆవాస్ యోజన", "పిఎమ్ ఆవాస్"],
            "mr": ["प्रधानमंत्री आवास योजना", "पीएम आवास"],
            "gu": ["પ્રધાનમંત્રી આવાસ યોજના", "પીએમ આવાસ"],
            "bn": ["প্রধানমন্ত্রী আবাস যোজনা", "পিএম আবাস"],
            "pa": ["ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਆਵਾਸ ਯੋਜਨਾ", "ਪੀਐਮ ਆਵਾਸ"],
            "ml": ["പ്രധാനമന്ത്രി ആവാസ് യോജന", "പിഎം ആവാസ്"],
            "or": ["ପ୍ରଧାନମନ୍ତ୍ରୀ ଆବାସ ଯୋଜନା", "ପିଏମ୍ ଆବାସ"],
            "as": ["প্ৰধানমন্ত্ৰী আবাস যোজনা", "পিএম আবাস"]
        }
    },
    {
        "name": "Jal Jeevan Mission",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Provides functional household tap connections to every rural household by 2024",
        "tags": ["Water Supply", "Rural Development", "Infrastructure"],
        "regional_names": {
            "hi": ["जल जीवन मिशन", "जल मिशन", "हर घर जल"],
            "kn": ["ಜಲ ಜೀವನ್ ಮಿಷನ್", "ಜಲ ಮಿಷನ್"],
            "ta": ["ஜல் ஜீவன் மிஷன்", "ஜல் மிஷன்"],
            "te": ["జల్ జీవన్ మిషన్", "జల్ మిషన్"],
            "mr": ["जल जीवन मिशन", "जल मिशन"],
            "gu": ["જલ જીવન મિશન", "જલ મિશન"],
            "bn": ["জল জীবন মিশন", "জল মিশন"],
            "pa": ["ਜਲ ਜੀਵਨ ਮਿਸ਼ਨ", "ਜਲ ਮਿਸ਼ਨ"],
            "ml": ["ജൽ ജീവൻ മിഷൻ", "ജൽ മിഷൻ"],
            "or": ["ଜଲ ଜୀବନ ମିଶନ", "ଜଲ ମିଶନ"],
            "as": ["জল জীৱন মিছন", "জল মিছন"]
        }
    },
    {
        "name": "Pradhan Mantri Mudra Yojana (PMMY)",
        "ministry": "Ministry Of Finance",
        "description": "Provides loans up to ₹10 lakh to non-corporate, non-farm small/micro enterprises",
        "tags": ["MSME", "Loans", "Entrepreneurship"],
        "regional_names": {
            "hi": ["मुद्रा योजना", "प्रधानमंत्री मुद्रा योजना", "पीएम मुद्रा"],
            "kn": ["ಮುದ್ರಾ ಯೋಜನೆ", "ಪ್ರಧಾನಮಂತ್ರಿ ಮುದ್ರಾ"],
            "ta": ["முத்ரா திட்டம்", "பிரதமர் முத்ரா"],
            "te": ["ముద్ర యోజన", "ప్రధానమంత్రి ముద్ర"],
            "mr": ["मुद्रा योजना", "प्रधानमंत्री मुद्रा"],
            "gu": ["મુદ્રા યોજના", "પ્રધાનમંત્રી મુદ્રા"],
            "bn": ["মুদ্রা যোজনা", "প্রধানমন্ত্রী মুদ্রা"],
            "pa": ["ਮੁਦਰਾ ਯੋਜਨਾ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਮੁਦਰਾ"],
            "ml": ["മുദ്ര യോജന", "പ്രധാനമന്ത്രി മുദ്ര"],
            "or": ["ମୁଦ୍ରା ଯୋଜନା", "ପ୍ରଧାନମନ୍ତ୍ରୀ ମୁଦ୍ରା"],
            "as": ["মুদ্ৰা যোজনা", "প্ৰধানমন্ত্ৰী মুদ্ৰা"]
        }
    },
    {
        "name": "Digital India",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Programme to transform India into digitally empowered society and knowledge economy",
        "tags": ["Digital Transformation", "E-Governance", "Technology"],
        "regional_names": {
            "hi": ["डिजिटल इंडिया", "डिजिटल भारत"],
            "kn": ["ಡಿಜಿಟಲ್ ಇಂಡಿಯಾ", "ಡಿಜಿಟಲ್ ಭಾರತ"],
            "ta": ["டிஜிட்டல் இந்தியா", "டிஜிட்டல் பாரத்"],
            "te": ["డిజిటల్ ఇండియా", "డిజిటల్ భారత్"],
            "mr": ["डिजिटल इंडिया", "डिजिटल भारत"],
            "gu": ["ડિજિટલ ઇન્ડિયા", "ડિજિટલ ભારત"],
            "bn": ["ডিজিটাল ইন্ডিয়া", "ডিজিটাল ভারত"],
            "pa": ["ਡਿਜੀਟਲ ਇੰਡੀਆ", "ਡਿਜੀਟਲ ਭਾਰਤ"],
            "ml": ["ഡിജിറ്റൽ ഇന്ത്യ", "ഡിജിറ്റൽ ഭാരത്"],
            "or": ["ଡିଜିଟାଲ ଇଣ୍ଡିଆ", "ଡିଜିଟାଲ ଭାରତ"],
            "as": ["ডিজিটেল ইণ্ডিয়া", "ডিজিটেল ভাৰত"]
        }
    },
    {
        "name": "Swachh Bharat Mission",
        "ministry": "Ministry Of Jal Shakti",
        "description": "National cleanliness campaign covering urban and rural areas to eliminate open defecation",
        "tags": ["Sanitation", "Cleanliness", "ODF"],
        "regional_names": {
            "hi": ["स्वच्छ भारत मिशन", "स्वच्छ भारत अभियान", "स्वच्छता अभियान"],
            "kn": ["ಸ್ವಚ್ಛ ಭಾರತ್ ಮಿಷನ್", "ಸ್ವಚ್ಛ ಭಾರತ್"],
            "ta": ["சுவச்ச பாரத் மிஷன்", "சுத்தம் பாரத்"],
            "te": ["స్వచ్ఛ భారత్ మిషన్", "స్వచ్ఛ భారత్"],
            "mr": ["स्वच्छ भारत मिशन", "स्वच्छता अभियान"],
            "gu": ["સ્વચ્છ ભારત મિશન", "સ્વચ્છતા અભિયાન"],
            "bn": ["স্বচ্ছ ভারত মিশন", "স্বচ্ছতা অভিযান"],
            "pa": ["ਸਵੱਛ ਭਾਰਤ ਮਿਸ਼ਨ", "ਸਫਾਈ ਮੁਹਿੰਮ"],
            "ml": ["സ്വച്ഛ് ഭാരത് മിഷൻ", "സ്വച്ഛത മിഷൻ"],
            "or": ["ସ୍ୱଚ୍ଛ ଭାରତ ମିଶନ", "ସ୍ୱଚ୍ଛତା ଅଭିଯାନ"],
            "as": ["স্বচ্ছ ভাৰত মিছন", "স্বচ্ছতা অভিযান"]
        }
    },
    {
        "name": "Make In India",
        "ministry": "Ministry Of Commerce and Industry",
        "description": "Initiative to encourage companies to manufacture in India and increase FDI",
        "tags": ["Manufacturing", "FDI", "Industrial Development"],
        "regional_names": {
            "hi": ["मेक इन इंडिया", "भारत में बनाओ"],
            "kn": ["ಮೇಕ್ ಇನ್ ಇಂಡಿಯಾ", "ಭಾರತದಲ್ಲಿ ತಯಾರಿಸಿ"],
            "ta": ["மேக் இன் இந்தியா", "இந்தியாவில் தயாரிக்கவும்"],
            "te": ["మేక్ ఇన్ ఇండియా", "భారతదేశంలో తయారు చేయండి"],
            "mr": ["मेक इन इंडिया", "भारतात बनवा"],
            "gu": ["મેક ઇન ઇન્ડિયા", "ભારતમાં બનાવો"],
            "bn": ["মেক ইন ইন্ডিয়া", "ভারতে তৈরি"],
            "pa": ["ਮੇਕ ਇਨ ਇੰਡੀਆ", "ਭਾਰਤ ਵਿੱਚ ਬਣਾਓ"],
            "ml": ["മേക്ക് ഇൻ ഇന്ത്യ", "ഇന്ത്യയിൽ നിർമ്മിക്കുക"],
            "or": ["ମେକ ଇନ ଇଣ୍ଡିଆ", "ଭାରତରେ ତିଆରି"],
            "as": ["মেক ইন ইণ্ডিয়া", "ভাৰতত নিৰ্মাণ"]
        }
    },
    {
        "name": "Startup India",
        "ministry": "Department for Promotion of Industry and Internal Trade",
        "description": "Initiative to build strong ecosystem for nurturing innovation and startups",
        "tags": ["Startups", "Innovation", "Entrepreneurship"],
        "regional_names": {
            "hi": ["स्टार्टअप इंडिया", "स्टार्टअप भारत"],
            "kn": ["ಸ್ಟಾರ್ಟಪ್ ಇಂಡಿಯಾ", "ಸ್ಟಾರ್ಟಪ್ ಭಾರತ"],
            "ta": ["ஸ்டார்ட்அப் இந்தியா", "ஸ்டார்ட்அப் பாரத்"],
            "te": ["స్టార్టప్ ఇండియా", "స్టార్టప్ భారత్"],
            "mr": ["स्टार्टअप इंडिया", "स्टार्टअप भारत"],
            "gu": ["સ્ટાર્ટઅપ ઇન્ડિયા", "સ્ટાર્ટઅપ ભારત"],
            "bn": ["স্টার্টআপ ইন্ডিয়া", "স্টার্টআপ ভারত"],
            "pa": ["ਸਟਾਰਟਅੱਪ ਇੰਡੀਆ", "ਸਟਾਰਟਅੱਪ ਭਾਰਤ"],
            "ml": ["സ്റ്റാർട്ടപ്പ് ഇന്ത്യ", "സ്റ്റാർട്ടപ്പ് ഭാരത്"],
            "or": ["ଷ୍ଟାର୍ଟଅପ ଇଣ୍ଡିଆ", "ଷ୍ଟାର୍ଟଅପ ଭାରତ"],
            "as": ["ষ্টাৰ্টআপ ইণ্ডিয়া", "ষ্টাৰ্টআপ ভাৰত"]
        }
    },
    {
        "name": "Skill India Mission",
        "ministry": "Ministry Of Skill Development and Entrepreneurship",
        "description": "Campaign to train 40 crore people in India with different skills by 2022",
        "tags": ["Skill Development", "Training", "Employment"],
        "regional_names": {
            "hi": ["स्किल इंडिया", "कौशल भारत", "कौशल विकास"],
            "kn": ["ಸ್ಕಿಲ್ ಇಂಡಿಯಾ", "ಕೌಶಲ್ಯ ಭಾರತ"],
            "ta": ["ஸ்கில் இந்தியா", "திறன் வளர்ச்சி"],
            "te": ["స్కిల్ ఇండియా", "నైపుణ్య భారత్"],
            "mr": ["स्किल इंडिया", "कौशल्य भारत"],
            "gu": ["સ્કિલ ઇન્ડિયા", "કૌશલ્ય ભારત"],
            "bn": ["স্কিল ইন্ডিয়া", "দক্ষতা ভারত"],
            "pa": ["ਸਕਿੱਲ ਇੰਡੀਆ", "ਹੁਨਰ ਭਾਰਤ"],
            "ml": ["സ്കിൽ ഇന്ത്യ", "കഴിവ് ഭാരത്"],
            "or": ["ସ୍କିଲ ଇଣ୍ଡିଆ", "ଦକ୍ଷତା ଭାରତ"],
            "as": ["স্কিল ইণ্ডিয়া", "দক্ষতা ভাৰত"]
        }
    },
    {
        "name": "Pradhan Mantri Jan Dhan Yojana",
        "ministry": "Ministry Of Finance",
        "description": "National Mission on Financial Inclusion ensuring access to financial services",
        "tags": ["Financial Inclusion", "Banking", "Insurance"],
        "regional_names": {
            "hi": ["जन धन योजना", "प्रधानमंत्री जन धन योजना", "पीएम जन धन"],
            "kn": ["ಜನ ಧನ ಯೋಜನೆ", "ಪ್ರಧಾನಮಂತ್ರಿ ಜನ ಧನ"],
            "ta": ["ஜன் தன் திட்டம்", "பிரதமர் ஜன் தன்"],
            "te": ["జన్ ధన్ యోజన", "ప్రధానమంత్రి జన్ ధన్"],
            "mr": ["जन धन योजना", "प्रधानमंत्री जन धन"],
            "gu": ["જન ધન યોજના", "પ્રધાનમંત્રી જન ધન"],
            "bn": ["জন ধন যোজনা", "প্রধানমন্ত্রী জন ধন"],
            "pa": ["ਜਨ ਧਨ ਯੋਜਨਾ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਜਨ ਧਨ"],
            "ml": ["ജൻ ധൻ യോജന", "പ്രധാനമന്ത്രി ജൻ ധൻ"],
            "or": ["ଜନ ଧନ ଯୋଜନା", "ପ୍ରଧାନମନ୍ତ୍ରୀ ଜନ ଧନ"],
            "as": ["জন ধন যোজনা", "প্ৰধানমন্ত্ৰী জন ধন"]
        }
    },
    {
        "name": "Atal Pension Yojana",
        "ministry": "Ministry Of Finance",
        "description": "Pension scheme for workers in unorganised sector",
        "tags": ["Pension", "Social Security", "Unorganised Sector"],
        "regional_names": {
            "hi": ["अटल पेंशन योजना", "एपीवाई", "अटल पेंशन"],
            "kn": ["ಅಟಲ್ ಪಿಂಚಣಿ ಯೋಜನೆ", "ಅಟಲ್ ಪಿಂಚಣಿ"],
            "ta": ["அடல் ஓய்வூதிய திட்டம்", "அடல் பென்ஷன்"],
            "te": ["అటల్ పెన్షన్ యోజన", "అటల్ పెన్షన్"],
            "mr": ["अटल पेन्शन योजना", "अटल पेन्शन"],
            "gu": ["અટલ પેન્શન યોજના", "અટલ પેન્શન"],
            "bn": ["অটল পেনশন যোজনা", "অটল পেনশন"],
            "pa": ["ਅਟਲ ਪੈਨਸ਼ਨ ਯੋਜਨਾ", "ਅਟਲ ਪੈਨਸ਼ਨ"],
            "ml": ["അടൽ പെൻഷൻ യോജന", "അടൽ പെൻഷൻ"],
            "or": ["ଅଟଲ ପେନସନ ଯୋଜନା", "ଅଟଲ ପେନସନ"],
            "as": ["অটল পেঞ্চন যোজনা", "অটল পেঞ্চন"]
        }
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Crop insurance scheme for farmers against crop loss",
        "tags": ["Agriculture", "Insurance", "Farmers", "Crop Protection"],
        "regional_names": {
            "hi": ["फसल बीमा योजना", "प्रधानमंत्री फसल बीमा योजना", "पीएम फसल बीमा"],
            "kn": ["ಫಸಲ್ ಬೀಮಾ ಯೋಜನೆ", "ಪ್ರಧಾನಮಂತ್ರಿ ಫಸಲ್ ಬೀಮಾ"],
            "ta": ["பயிர் காப்பீட்டு திட்டம்", "பிரதமர் பயிர் காப்பீடு"],
            "te": ["పంట బీమా యోజన", "ప్రధానమంత్రి పంట బీమా"],
            "mr": ["पीक विमा योजना", "प्रधानमंत्री फसल विमा"],
            "gu": ["પાક વીમા યોજના", "પ્રધાનમંત્રી ફસલ વીમા"],
            "bn": ["ফসল বীমা যোজনা", "প্রধানমন্ত্রী ফসল বীমা"],
            "pa": ["ਫਸਲ ਬੀਮਾ ਯੋਜਨਾ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਫਸਲ ਬੀਮਾ"],
            "ml": ["വിള ഇൻഷുറൻസ് യോജന", "പ്രധാനമന്ത്രി ഫസൽ ബീമ"],
            "or": ["ଫସଲ ବୀମା ଯୋଜନା", "ପ୍ରଧାନମନ୍ତ୍ରୀ ଫସଲ ବୀମା"],
            "as": ["শস্য বীমা যোজনা", "প্ৰধানমন্ত্ৰী ফচল বীমা"]
        }
    },
    {
        "name": "National Health Mission",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Provides accessible, affordable and quality health care to rural and urban population",
        "tags": ["Health", "Healthcare Infrastructure", "Rural Health"],
        "regional_names": {
            "hi": ["राष्ट्रीय स्वास्थ्य मिशन", "स्वास्थ्य मिशन", "एनएचएम"],
            "kn": ["ರಾಷ್ಟ್ರೀಯ ಆರೋಗ್ಯ ಮಿಷನ್", "ಆರೋಗ್ಯ ಮಿಷನ್"],
            "ta": ["தேசிய சுகாதார திட்டம்", "சுகாதார மிஷன்"],
            "te": ["జాతీయ ఆరోగ్య మిషన్", "ఆరోగ్య మిషన్"],
            "mr": ["राष्ट्रीय आरोग्य मिशन", "आरोग्य मिशन"],
            "gu": ["રાષ્ટ્રીય આરોગ્ય મિશન", "આરોગ્ય મિશન"],
            "bn": ["জাতীয় স্বাস্থ্য মিশন", "স্বাস্থ্য মিশন"],
            "pa": ["ਰਾਸ਼ਟਰੀ ਸਿਹਤ ਮਿਸ਼ਨ", "ਸਿਹਤ ਮਿਸ਼ਨ"],
            "ml": ["ദേശീയ ആരോഗ്യ മിഷൻ", "ആരോഗ്യ മിഷൻ"],
            "or": ["ଜାତୀୟ ସ୍ୱାସ୍ଥ୍ୟ ମିଶନ", "ସ୍ୱାସ୍ଥ୍ୟ ମିଶନ"],
            "as": ["ৰাষ্ট্ৰীয় স্বাস্থ্য মিছন", "স্বাস্থ্য মিছন"]
        }
    },
    {
        "name": "Beti Bachao Beti Padhao",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Scheme to address declining Child Sex Ratio and empower girl child",
        "tags": ["Girl Child", "Women Empowerment", "Education"],
        "regional_names": {
            "hi": ["बेटी बचाओ बेटी पढ़ाओ", "बेटी बचाओ", "बेटी पढ़ाओ"],
            "kn": ["ಬೇಟಿ ಬಚಾಓ ಬೇಟಿ ಪಡಾಓ", "ಹೆಣ್ಣು ಮಗುವನ್ನು ಉಳಿಸಿ ಶಿಕ್ಷಣ ನೀಡಿ"],
            "ta": ["பெட்டி பசாவோ பெட்டி படாவோ", "பெண் குழந்தையை காப்பாற்று கல்வி அளி"],
            "te": ["బేటీ బచావో బేటీ పడావో", "ఆడపిల్లను రక్షించండి చదివించండి"],
            "mr": ["बेटी बचाओ बेटी पढवा", "मुलगी वाचवा"],
            "gu": ["બેટી બચાવો બેટી પઢાવો", "દીકરી બચાવો શિક્ષણ આપો"],
            "bn": ["বেটি বাঁচাও বেটি পড়াও", "মেয়ে বাঁচাও পড়াও"],
            "pa": ["ਬੇਟੀ ਬਚਾਓ ਬੇਟੀ ਪੜ੍ਹਾਓ", "ਧੀ ਬਚਾਓ ਪੜ੍ਹਾਓ"],
            "ml": ["ബേട്ടി ബചാവോ ബേട്ടി പഢാവോ", "പെൺകുട്ടിയെ സംരക്ഷിക്കുക പഠിപ്പിക്കുക"],
            "or": ["ବେଟି ବଚାଓ ବେଟି ପଢାଓ", "ଝିଅ ବଞ୍ଚାଅ ପଢାଅ"],
            "as": ["বেটী বাচাও বেটী পঢ়াও", "ছোৱালী বচাওক পঢ়াওক"]
        }
    },
    {
        "name": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee Act)",
        "ministry": "Ministry Of Rural Development",
        "description": "Guarantees 100 days of wage employment to rural households",
        "tags": ["Rural Employment", "Wage Employment", "Social Security"],
        "regional_names": {
            "hi": ["मनरेगा", "महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम", "नरेगा", "100 दिन रोजगार"],
            "kn": ["ಎಂಜಿಎನ್‌ಆರ್‌ಇಜಿಎ", "ಮಹಾತ್ಮಾ ಗಾಂಧಿ ರಾಷ್ಟ್ರೀಯ ಗ್ರಾಮೀಣ ಉದ್ಯೋಗ ಖಾತರಿ ಕಾಯಿದೆ", "ನರೇಗಾ"],
            "ta": ["எம்ஜிஎன்ஆர்இஜிஏ", "மகாத்மா காந்தி தேசிய ஊரக வேலைவாய்ப்பு உத்தரவாதம்", "நரேகா"],
            "te": ["ఎంజిఎన్‌ఆర్‌ఈజిఏ", "మహాత్మా గాంధీ జాతీయ గ్రామీణ ఉపాధి హామీ చట్టం", "నరేగా"],
            "mr": ["मनरेगा", "महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार हमी कायदा", "नरेगा"],
            "gu": ["મનરેગા", "મહાત્મા ગાંધી રાષ્ટ્રીય ગ્રામીણ રોજગાર ગેરંટી કાયદો", "નરેગા"],
            "bn": ["মনরেগা", "মহাত্মা গান্ধী জাতীয় গ্রামীণ কর্মসংস্থান গ্যারান্টি আইন", "নরেগা"],
            "pa": ["ਮਨਰੇਗਾ", "ਮਹਾਤਮਾ ਗਾਂਧੀ ਰਾਸ਼ਟਰੀ ਪੇਂਡੂ ਰੁਜ਼ਗਾਰ ਗਾਰੰਟੀ ਐਕਟ", "ਨਰੇਗਾ"],
            "ml": ["എംജിഎൻആർഇജിഎ", "മഹാത്മാഗാന്ധി ദേശീയ ഗ്രാമീണ തൊഴിൽ ഉറപ്പ് നിയമം", "നരേഗ"],
            "or": ["ମନରେଗା", "ମହାତ୍ମା ଗାନ୍ଧୀ ଜାତୀୟ ଗ୍ରାମୀଣ ନିଯୁକ୍ତି ଗ୍ୟାରେଣ୍ଟି ଆକ୍ଟ", "ନରେଗା"],
            "as": ["মনৰেগা", "মহাত্মা গান্ধী ৰাষ্ট্ৰীয় গ্ৰাম্য নিয়োগ নিশ্চয়তা আইন", "নৰেগা"]
        }
    },
    {
        "name": "National Education Policy 2020",
        "ministry": "Ministry Of Education",
        "description": "Comprehensive framework for elementary to higher education",
        "tags": ["Education Reform", "Policy", "Skill Development"],
        "regional_names": {
            "hi": ["राष्ट्रीय शिक्षा नीति", "एनईपी 2020", "शिक्षा नीति"],
            "kn": ["ರಾಷ್ಟ್ರೀಯ ಶಿಕ್ಷಣ ನೀತಿ", "ಎನ್‌ಇಪಿ 2020"],
            "ta": ["தேசிய கல்வி கொள்கை", "என்இபி 2020"],
            "te": ["జాతీయ విద్యా విధానం", "ఎన్‌ఈపి 2020"],
            "mr": ["राष्ट्रीय शिक्षण धोरण", "एनईपी 2020"],
            "gu": ["રાષ્ટ્રીય શિક્ષણ નીતિ", "એનઇપી 2020"],
            "bn": ["জাতীয় শিক্ষা নীতি", "এনইপি 2020"],
            "pa": ["ਰਾਸ਼ਟਰੀ ਸਿੱਖਿਆ ਨੀਤੀ", "ਐਨਈਪੀ 2020"],
            "ml": ["ദേശീയ വിദ്യാഭ്യാസ നയം", "എൻഇപി 2020"],
            "or": ["ଜାତୀୟ ଶିକ୍ଷା ନୀତି", "ଏନଇପି 2020"],
            "as": ["ৰাষ্ট্ৰীয় শিক্ষা নীতি", "এনইপি 2020"]
        }
    },
    {
        "name": "Pradhan Mantri Gram Sadak Yojana",
        "ministry": "Ministry Of Rural Development",
        "description": "Provides connectivity to unconnected habitations through good all-weather roads",
        "tags": ["Rural Roads", "Infrastructure", "Connectivity"],
        "regional_names": {
            "hi": ["प्रधानमंत्री ग्राम सड़क योजना", "पीएमजीएसवाई", "ग्राम सड़क योजना"],
            "kn": ["ಪ್ರಧಾನಮಂತ್ರಿ ಗ್ರಾಮ ಸಡಕ್ ಯೋಜನೆ", "ಗ್ರಾಮ ರಸ್ತೆ ಯೋಜನೆ"],
            "ta": ["பிரதமர் கிராம சாலை திட்டம்", "கிராம சாலை திட்டம்"],
            "te": ["ప్రధానమంత్రి గ్రామ సడక్ యోజన", "గ్రామ రహదారి పథకం"],
            "mr": ["प्रधानमंत्री ग्राम सडक योजना", "ग्रामीण रस्ता योजना"],
            "gu": ["પ્રધાનમંત્રી ગ્રામ સડક યોજના", "ગ્રામ રસ્તા યોજના"],
            "bn": ["প্রধানমন্ত্রী গ্রাম সড়ক যোজনা", "গ্রাম সড়ক যোজনা"],
            "pa": ["ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਗ੍ਰਾਮ ਸੜਕ ਯੋਜਨਾ", "ਪਿੰਡ ਸੜਕ ਯੋਜਨਾ"],
            "ml": ["പ്രധാനമന്ത്രി ഗ്രാമ സഡക് യോജന", "ഗ്രാമ റോഡ് യോജന"],
            "or": ["ପ୍ରଧାନମନ୍ତ୍ରୀ ଗ୍ରାମ ସଡକ ଯୋଜନା", "ଗ୍ରାମ ସଡକ ଯୋଜନା"],
            "as": ["প্ৰধানমন্ত্ৰী গ্ৰাম সড়ক যোজনা", "গ্ৰাম পথ যোজনা"]
        }
    },
    {
        "name": "Stand Up India",
        "ministry": "Ministry Of Finance",
        "description": "Facilitates bank loans between ₹10 lakh and ₹1 crore to SC/ST and women entrepreneurs",
        "tags": ["Entrepreneurship", "SC/ST", "Women", "Loans"],
        "regional_names": {
            "hi": ["स्टैंड अप इंडिया", "खड़े हो जाओ भारत"],
            "kn": ["ಸ್ಟಾಂಡ್ ಅಪ್ ಇಂಡಿಯಾ", "ಎದ್ದು ನಿಲ್ಲಿ ಭಾರತ"],
            "ta": ["ஸ்டாண்ட் அப் இந்தியா", "எழுந்து நில் இந்தியா"],
            "te": ["స్టాండ్ అప్ ఇండియా", "నిలబడు భారతం"],
            "mr": ["स्टँड अप इंडिया", "उभे राहा भारत"],
            "gu": ["સ્ટેન્ડ અપ ઇન્ડિયા", "ઉભા રહો ભારત"],
            "bn": ["স্ট্যান্ড আপ ইন্ডিয়া", "দাঁড়াও ভারত"],
            "pa": ["ਸਟੈਂਡ ਅੱਪ ਇੰਡੀਆ", "ਖੜੇ ਹੋਵੋ ਭਾਰਤ"],
            "ml": ["സ്റ്റാൻഡ് അപ്പ് ഇന്ത്യ", "എഴുന്നേൽക്കൂ ഭാരതം"],
            "or": ["ଷ୍ଟାଣ୍ଡ ଅପ ଇଣ୍ଡିଆ", "ଠିଆ ହୁଅ ଭାରତ"],
            "as": ["ষ্টেণ্ড আপ ইণ্ডিয়া", "থিয় হোৱা ভাৰত"]
        }
    },
    {
        "name": "PMEGP (Prime Minister's Employment Generation Programme)",
        "ministry": "Ministry Of Micro, Small and Medium Enterprises",
        "description": "Credit linked subsidy programme for generating self-employment",
        "tags": ["Self Employment", "MSME", "Subsidy"],
        "regional_names": {
            "hi": ["पीएमईजीपी", "प्रधानमंत्री रोजगार सृजन कार्यक्रम", "रोजगार सृजन योजना"],
            "kn": ["ಪಿಎಂಇಜಿಪಿ", "ಪ್ರಧಾನಮಂತ್ರಿ ಉದ್ಯೋಗ ಸೃಷ್ಟಿ ಕಾರ್ಯಕ್ರಮ"],
            "ta": ["பிஎம்இஜிபி", "பிரதமர் வேலைவாய்ப்பு உருவாக்க திட்டம்"],
            "te": ["పిఎంఈజిపి", "ప్రధానమంత్రి ఉపాధి కల్పన కార్యక్రమం"],
            "mr": ["पीएमईजीपी", "प्रधानमंत्री रोजगार निर्मिती कार्यक्रम"],
            "gu": ["પીએમઇજીપી", "પ્રધાનમંત્રી રોજગાર સર્જન કાર્યક્રમ"],
            "bn": ["পিএমইজিপি", "প্রধানমন্ত্রী কর্মসংস্থান সৃষ্টি কর্মসূচি"],
            "pa": ["ਪੀਐਮਈਜੀਪੀ", "ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਰੁਜ਼ਗਾਰ ਪੈਦਾ ਪ੍ਰੋਗਰਾਮ"],
            "ml": ["പിഎംഇജിപി", "പ്രധാനമന്ത്രി തൊഴിൽ സൃഷ്ടി പരിപാടി"],
            "or": ["ପିଏମଇଜିପି", "ପ୍ରଧାନମନ୍ତ୍ରୀ ନିଯୁକ୍ତି ସୃଷ୍ଟି କାର୍ଯ୍ୟକ୍ରମ"],
            "as": ["পিএমইজিপি", "প্ৰধানমন্ত্ৰী নিয়োগ সৃষ্টি কাৰ্যসূচী"]
        }
    },
    {
        "name": "National Rural Livelihood Mission (NRLM)",
        "ministry": "Ministry Of Rural Development",
        "description": "Poverty alleviation project to create efficient and effective institutional platforms for rural poor",
        "tags": ["Rural Livelihood", "Poverty Alleviation", "SHG"],
        "regional_names": {
            "hi": ["राष्ट्रीय ग्रामीण आजीविका मिशन", "एनआरएलएम", "आजीविका मिशन", "दीनदयाल अंत्योदय योजना"],
            "kn": ["ರಾಷ್ಟ್ರೀಯ ಗ್ರಾಮೀಣ ಜೀವನೋಪಾಯ ಮಿಷನ್", "ಎನ್‌ಆರ್‌ಎಲ್‌ಎಂ"],
            "ta": ["தேசிய கிராமப்புற வாழ்வாதார திட்டம்", "என்ஆர்எல்எம்"],
            "te": ["జాతీయ గ్రామీణ జీవనోపాధి మిషన్", "ఎన్‌ఆర్‌ఎల్‌ఎమ్"],
            "mr": ["राष्ट्रीय ग्रामीण उपजीविका मिशन", "एनआरएलएम"],
            "gu": ["રાષ્ટ્રીય ગ્રામીણ જીવનનિર્વાહ મિશન", "એનઆરએલએમ"],
            "bn": ["জাতীয় গ্রামীণ জীবিকা মিশন", "এনআরএলএম"],
            "pa": ["ਰਾਸ਼ਟਰੀ ਪੇਂਡੂ ਰੋਜ਼ੀ-ਰੋਟੀ ਮਿਸ਼ਨ", "ਐਨਆਰਐਲਐਮ"],
            "ml": ["ദേശീയ ഗ്രാമീണ ഉപജീവന മിഷൻ", "എൻആർഎൽഎം"],
            "or": ["ଜାତୀୟ ଗ୍ରାମୀଣ ଜୀବିକା ମିଶନ", "ଏନଆରଏଲଏମ"],
            "as": ["ৰাষ্ট্ৰীয় গ্ৰাম্য জীৱিকা মিছন", "এনআৰএলএম"]
        }
    },
    {
        "name": "Pradhan Mantri Matru Vandana Yojana",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Maternity benefit programme providing cash incentive to pregnant and lactating women",
        "tags": ["Maternity", "Women Welfare", "Child Nutrition"],
        "regional_names": {
            "hi": ["प्रधानमंत्री मातृ वंदना योजना", "पीएममेवीवाई", "मातृत्व योजना"],
            "kn": ["ಪ್ರಧಾನಮಂತ್ರಿ ಮಾತೃ ವಂದನಾ ಯೋಜನೆ", "ಮಾತೃತ್ವ ಯೋಜನೆ"],
            "ta": ["பிரதமர் மாதர் வந்தனா திட்டம்", "தாய்மை நல திட்டம்"],
            "te": ["ప్రధానమంత్రి మాతృ వందనా యోజన", "మాతృత్వ యోజన"],
            "mr": ["प्रधानमंत्री मातृ वंदना योजना", "मातृत्व योजना"],
            "gu": ["પ્રધાનમંત્રી માતૃ વંદના યોજના", "માતૃત્વ યોજના"],
            "bn": ["প্রধানমন্ত্রী মাতৃ বন্দনা যোজনা", "মাতৃত্ব যোজনা"],
            "pa": ["ਪ੍ਰਧਾਨ ਮੰਤਰੀ ਮਾਤ੍ਰੂ ਵੰਦਨਾ ਯੋਜਨਾ", "ਮਾਤ੍ਰਿਤਵ ਯੋਜਨਾ"],
            "ml": ["പ്രധാനമന്ത്രി മാതൃ വന്ദന യോജന", "മാതൃത്വ യോജന"],
            "or": ["ପ୍ରଧାନମନ୍ତ୍ରୀ ମାତୃ ବନ୍ଦନା ଯୋଜନା", "ମାତୃତ୍ୱ ଯୋଜନା"],
            "as": ["প্ৰধানমন্ত্ৰী মাতৃ বন্দনা যোজনা", "মাতৃত্ব যোজনা"]
        }
    },
    {
        "name": "Mid-Day Meal Scheme",
        "ministry": "Ministry Of Education",
        "description": "Provides free lunch to children in government and government-aided schools",
        "tags": ["Child Nutrition", "Education", "Food Security"]
    },
    {
        "name": "Rashtriya Uchchatar Shiksha Abhiyan (RUSA)",
        "ministry": "Ministry Of Education",
        "description": "Centrally Sponsored Scheme for improving access, equity and quality in higher education",
        "tags": ["Higher Education", "Quality Improvement", "Infrastructure"]
    },
    {
        "name": "National Social Assistance Programme (NSAP)",
        "ministry": "Ministry Of Rural Development",
        "description": "Social security for elderly, widows and disabled persons through pension schemes",
        "tags": ["Social Security", "Pension", "Elderly", "Disabled"]
    },
    {
        "name": "Pradhan Mantri Suraksha Bima Yojana",
        "ministry": "Ministry Of Finance",
        "description": "Accidental insurance scheme offering coverage of ₹2 lakh at premium of ₹12 per annum",
        "tags": ["Insurance", "Accident Coverage", "Financial Security"]
    },
    {
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
        "ministry": "Ministry Of Finance",
        "description": "Life insurance scheme offering coverage of ₹2 lakh at premium of ₹330 per annum",
        "tags": ["Life Insurance", "Financial Security"]
    },
    {
        "name": "Saubhagya Yojana (Pradhan Mantri Sahaj Bijli Har Ghar Yojana)",
        "ministry": "Ministry Of Power",
        "description": "Universal household electrification scheme",
        "tags": ["Electrification", "Power", "Rural Development"]
    },
    {
        "name": "UDAN (Ude Desh ka Aam Naagrik)",
        "ministry": "Ministry Of Civil Aviation",
        "description": "Regional connectivity scheme to make air travel affordable",
        "tags": ["Aviation", "Regional Connectivity", "Transport"]
    },
    {
        "name": "Namami Gange Programme",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Integrated conservation mission for rejuvenation of river Ganga",
        "tags": ["River Rejuvenation", "Environment", "Water Conservation"]
    },
    {
        "name": "Smart Cities Mission",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Develops 100 cities as model cities with core infrastructure and quality life",
        "tags": ["Urban Development", "Smart Cities", "Infrastructure"]
    },
    {
        "name": "AMRUT (Atal Mission for Rejuvenation and Urban Transformation)",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Ensures basic services to households and builds amenities in cities",
        "tags": ["Urban Infrastructure", "Water Supply", "Sewerage"]
    },
    {
        "name": "National Infrastructure Pipeline",
        "ministry": "Ministry Of Finance",
        "description": "₹111 lakh crore investment plan for infrastructure development",
        "tags": ["Infrastructure", "Investment", "Development"]
    },
    {
        "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)",
        "ministry": "Ministry Of Skill Development and Entrepreneurship",
        "description": "Flagship scheme for skill training of youth",
        "tags": ["Skill Training", "Youth", "Employment"]
    },
    {
        "name": "National Apprenticeship Promotion Scheme",
        "ministry": "Ministry Of Skill Development and Entrepreneurship",
        "description": "Promotes apprenticeship training and increases engagement with industry",
        "tags": ["Apprenticeship", "Industrial Training", "Employment"]
    },
    {
        "name": "PM SVANidhi (Pradhan Mantri Street Vendor's Atma Nirbhar Nidhi)",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Micro-credit scheme for street vendors",
        "tags": ["Street Vendors", "Credit", "Urban Poor"]
    },
    {
        "name": "Ayushman Bharat Health and Wellness Centres",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Upgrades sub-centres and primary health centres to provide comprehensive healthcare",
        "tags": ["Primary Healthcare", "Health Infrastructure", "Wellness"]
    },
    {
        "name": "Poshan Abhiyaan (National Nutrition Mission)",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Holistic approach to prevent and reduce malnutrition",
        "tags": ["Nutrition", "Child Health", "Malnutrition"]
    },
    {
        "name": "National Food Security Mission",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Increases production of rice, wheat, pulses and coarse cereals",
        "tags": ["Food Security", "Agriculture", "Crop Production"]
    },
    {
        "name": "Paramparagat Krishi Vikas Yojana",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Promotes organic farming and soil health management",
        "tags": ["Organic Farming", "Sustainable Agriculture", "Soil Health"]
    },
    {
        "name": "Pradhan Mantri Krishi Sinchai Yojana",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Expands cultivable area with assured irrigation and improves water use efficiency",
        "tags": ["Irrigation", "Water Management", "Agriculture"]
    },
    {
        "name": "e-NAM (National Agriculture Market)",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Pan-India electronic trading portal for agricultural commodities",
        "tags": ["Agricultural Marketing", "Digital Platform", "Price Discovery"]
    },
    {
        "name": "Kisan Credit Card",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Provides timely credit support for agriculture and allied activities",
        "tags": ["Agricultural Credit", "Farmers", "Banking"]
    },
    {
        "name": "Soil Health Card Scheme",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Provides soil nutrient status to farmers for judicious use of fertilizers",
        "tags": ["Soil Health", "Agriculture", "Fertilizers"]
    },
    {
        "name": "National Mission on Edible Oils - Oil Palm",
        "ministry": "Ministry Of Agriculture and Farmers Welfare",
        "description": "Promotes oil palm cultivation to reduce import dependency",
        "tags": ["Oilseeds", "Import Substitution", "Agriculture"]
    },
    {
        "name": "PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan)",
        "ministry": "Ministry Of New and Renewable Energy",
        "description": "Supports installation of solar pumps and grid connected solar power plants",
        "tags": ["Solar Energy", "Agriculture", "Renewable Energy"]
    },
    {
        "name": "National Livestock Mission",
        "ministry": "Ministry Of Fisheries, Animal Husbandry and Dairying",
        "description": "Sustainable development of livestock sector",
        "tags": ["Livestock", "Animal Husbandry", "Dairy"]
    },
    {
        "name": "Pradhan Mantri Matsya Sampada Yojana",
        "ministry": "Ministry Of Fisheries, Animal Husbandry and Dairying",
        "description": "Sustainable and responsible development of fisheries sector",
        "tags": ["Fisheries", "Blue Revolution", "Aquaculture"]
    },
    {
        "name": "National Programme for Dairy Development",
        "ministry": "Ministry Of Fisheries, Animal Husbandry and Dairying",
        "description": "Creates and strengthens infrastructure for milk procurement, processing and marketing",
        "tags": ["Dairy Development", "Milk Production", "Cooperatives"]
    },
    {
        "name": "One Nation One Ration Card",
        "ministry": "Ministry Of Consumer Affairs, Food and Public Distribution",
        "description": "Enables portability of ration card benefits across the country",
        "tags": ["Food Security", "PDS", "Digital Integration"]
    },
    {
        "name": "Fortification of Rice in Public Distribution System",
        "ministry": "Ministry Of Consumer Affairs, Food and Public Distribution",
        "description": "Distributes fortified rice through PDS to combat malnutrition",
        "tags": ["Nutrition", "Food Fortification", "PDS"]
    },
    {
        "name": "National Clean Air Programme (NCAP)",
        "ministry": "Ministry Of Environment, Forest and Climate Change",
        "description": "Comprehensive plan to reduce air pollution across the country",
        "tags": ["Air Pollution", "Environment", "Public Health"]
    },
    {
        "name": "Green India Mission",
        "ministry": "Ministry Of Environment, Forest and Climate Change",
        "description": "Increases forest and tree cover and improves quality of existing forests",
        "tags": ["Afforestation", "Climate Change", "Environment"]
    },
    {
        "name": "National Solar Mission",
        "ministry": "Ministry Of New and Renewable Energy",
        "description": "Promotes solar energy for power generation and other applications",
        "tags": ["Solar Power", "Renewable Energy", "Clean Energy"]
    },
    {
        "name": "Production Linked Incentive (PLI) Scheme",
        "ministry": "Multiple Ministries",
        "description": "Incentivizes domestic manufacturing across 14 sectors",
        "tags": ["Manufacturing", "Make in India", "Incentives"]
    },
    {
        "name": "Atmanirbhar Bharat Rozgar Yojana",
        "ministry": "Ministry Of Labour and Employment",
        "description": "Incentivizes employers for creation of new employment along with social security benefits",
        "tags": ["Employment", "Social Security", "EPFO"]
    },
    {
        "name": "e-Shram Portal",
        "ministry": "Ministry Of Labour and Employment",
        "description": "National database of unorganised workers",
        "tags": ["Unorganised Workers", "Database", "Social Security"]
    },
    {
        "name": "PM CARES Fund",
        "ministry": "Prime Minister's Office",
        "description": "Public charitable trust for emergency and distress situations",
        "tags": ["Disaster Relief", "Healthcare", "Emergency Response"]
    },
    {
        "name": "Ayushman Bharat Digital Mission",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Creates digital health ecosystem with unique health IDs",
        "tags": ["Digital Health", "Health Records", "Technology"]
    },
    {
        "name": "PM-WANI (Wi-Fi Access Network Interface)",
        "ministry": "Ministry Of Communications",
        "description": "Framework for setting up public Wi-Fi hotspots",
        "tags": ["WiFi", "Digital Connectivity", "Internet Access"]
    },
    {
        "name": "BharatNet",
        "ministry": "Ministry Of Communications",
        "description": "Provides broadband connectivity to all gram panchayats",
        "tags": ["Broadband", "Rural Connectivity", "Digital Infrastructure"]
    },
    {
        "name": "National Knowledge Network",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Multi-gigabit nationwide network for educational and research institutions",
        "tags": ["Education Network", "Research", "High-Speed Internet"]
    },
    {
        "name": "SAMARTH UDYOG 4.0",
        "ministry": "Ministry Of Heavy Industries",
        "description": "Promotes adoption of Industry 4.0 technologies in MSMEs",
        "tags": ["Industry 4.0", "MSME", "Technology Adoption"]
    },
    {
        "name": "FAME India (Faster Adoption of Manufacturing of Electric Vehicles)",
        "ministry": "Ministry Of Heavy Industries",
        "description": "Promotes electric and hybrid vehicle technologies",
        "tags": ["Electric Vehicles", "Clean Transport", "Subsidy"]
    },
    {
        "name": "National Mission on Transformative Mobility and Battery Storage",
        "ministry": "NITI Aayog",
        "description": "Promotes clean, connected, shared and sustainable mobility",
        "tags": ["Electric Mobility", "Battery Technology", "Clean Transport"]
    },
    {
        "name": "National Hydrogen Mission",
        "ministry": "Ministry Of New and Renewable Energy",
        "description": "Makes India a global hub for production and export of green hydrogen",
        "tags": ["Green Hydrogen", "Clean Energy", "Energy Transition"]
    },
    {
        "name": "Jal Shakti Abhiyan",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Campaign for water conservation and water security",
        "tags": ["Water Conservation", "Rainwater Harvesting", "Groundwater Recharge"]
    },
    {
        "name": "Atal Bhujal Yojana",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Improves groundwater management in priority areas",
        "tags": ["Groundwater", "Water Management", "Community Participation"]
    },
    {
        "name": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana",
        "ministry": "Ministry Of Chemicals and Fertilizers",
        "description": "Provides quality generic medicines at affordable prices",
        "tags": ["Generic Medicines", "Healthcare", "Affordable Medicine"]
    },
    {
        "name": "Mission Indradhanush",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Immunization programme targeting children and pregnant women",
        "tags": ["Immunization", "Child Health", "Vaccination"]
    },
    {
        "name": "National Viral Hepatitis Control Programme",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Prevents and controls viral hepatitis in India",
        "tags": ["Hepatitis", "Disease Control", "Public Health"]
    },
    {
        "name": "National AIDS Control Programme",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Provides comprehensive HIV/AIDS prevention, care and treatment",
        "tags": ["HIV/AIDS", "Disease Control", "Healthcare"]
    },
    {
        "name": "National Programme for Prevention and Control of Cancer, Diabetes, CVD and Stroke",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Screening and management of non-communicable diseases",
        "tags": ["NCDs", "Disease Prevention", "Screening"]
    },
    {
        "name": "Rashtriya Bal Swasthya Karyakram",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Screening and early intervention for 4 'D's - Defects, Diseases, Deficiencies, Developmental delays",
        "tags": ["Child Health", "Screening", "Early Intervention"]
    },
    {
        "name": "Pradhan Mantri National Dialysis Programme",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Provides dialysis services in district hospitals",
        "tags": ["Dialysis", "Kidney Disease", "Healthcare"]
    },
    {
        "name": "National Tobacco Control Programme",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Prevents and controls tobacco consumption",
        "tags": ["Tobacco Control", "Public Health", "Disease Prevention"]
    },
    {
        "name": "Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB PM-JAY)",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "World's largest health insurance scheme covering 50 crore beneficiaries",
        "tags": ["Health Insurance", "Universal Health Coverage", "Healthcare Access"]
    },
    {
        "name": "National Programme for Control of Blindness and Visual Impairment",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Reduces prevalence of blindness through eye care services",
        "tags": ["Eye Care", "Blindness Prevention", "Healthcare"]
    },
    {
        "name": "National Mental Health Programme",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Ensures availability and accessibility of mental health care",
        "tags": ["Mental Health", "Healthcare", "Disease Management"]
    },
    {
        "name": "Integrated Child Development Services (ICDS)",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Provides nutrition, health and pre-school education to children under 6 years",
        "tags": ["Child Development", "Nutrition", "Early Childhood Education"]
    },
    {
        "name": "National Creche Scheme",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Day care facilities for children of working mothers",
        "tags": ["Childcare", "Working Mothers", "Day Care"]
    },
    {
        "name": "Scheme for Adolescent Girls (SAG)",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Addresses nutritional and health needs of adolescent girls",
        "tags": ["Adolescent Girls", "Nutrition", "Health"]
    },
    {
        "name": "Mission Shakti",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Umbrella scheme for women's safety, security and empowerment",
        "tags": ["Women Safety", "Empowerment", "Gender Justice"]
    },
    {
        "name": "Nirbhaya Fund",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Supports initiatives addressing women's safety",
        "tags": ["Women Safety", "Gender Violence", "Emergency Response"]
    },
    {
        "name": "One Stop Centre Scheme",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Support services to women affected by violence",
        "tags": ["Women Safety", "Violence Against Women", "Support Services"]
    },
    {
        "name": "Mahila Shakti Kendra",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Community level structures for rural women's empowerment",
        "tags": ["Women Empowerment", "Rural Women", "Community Support"]
    },
    {
        "name": "Pradhan Mantri Rashtriya Bal Puraskar",
        "ministry": "Ministry Of Women & Child Development",
        "description": "National award for exceptional children",
        "tags": ["Child Awards", "Recognition", "Talent"]
    },
    {
        "name": "CHILDLINE 1098",
        "ministry": "Ministry Of Women & Child Development",
        "description": "24-hour emergency phone service for children in distress",
        "tags": ["Child Protection", "Emergency Service", "Helpline"]
    },
    {
        "name": "National Child Labour Project",
        "ministry": "Ministry Of Labour and Employment",
        "description": "Rehabilitation of child labour through education",
        "tags": ["Child Labour", "Education", "Rehabilitation"]
    },
    {
        "name": "National Commission for Protection of Child Rights",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Monitors implementation of child rights laws",
        "tags": ["Child Rights", "Legal Protection", "Child Welfare"]
    },
    {
        "name": "Protection of Children from Sexual Offences (POCSO)",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Legal framework for protection of children from sexual abuse",
        "tags": ["Child Protection", "Sexual Abuse", "Legal Framework"]
    },
    {
        "name": "Pre-Matric Scholarship for SC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to SC students studying in classes IX and X",
        "tags": ["Scholarship", "SC Students", "Education"]
    },
    {
        "name": "Post-Matric Scholarship for SC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to SC students for post-matriculation studies",
        "tags": ["Scholarship", "SC Students", "Higher Education"]
    },
    {
        "name": "Pre-Matric Scholarship for OBC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to OBC students studying in classes IX and X",
        "tags": ["Scholarship", "OBC Students", "Education"]
    },
    {
        "name": "Post-Matric Scholarship for OBC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to OBC students for post-matriculation studies",
        "tags": ["Scholarship", "OBC Students", "Higher Education"]
    },
    {
        "name": "Pre-Matric Scholarship for Minority Communities",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Financial assistance to minority students studying in classes I to X",
        "tags": ["Scholarship", "Minority Students", "Education"]
    },
    {
        "name": "Post-Matric Scholarship for Minority Communities",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Financial assistance to minority students for post-matriculation studies",
        "tags": ["Scholarship", "Minority Students", "Higher Education"]
    },
    {
        "name": "Merit-cum-Means Based Scholarship for Minority Communities",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Merit-based scholarship for meritorious minority students",
        "tags": ["Scholarship", "Minority Students", "Merit Based"]
    },
    {
        "name": "Maulana Azad National Fellowship",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Fellowship for minority students pursuing M.Phil/Ph.D",
        "tags": ["Fellowship", "Minority Students", "Research"]
    },
    {
        "name": "Padho Pardesh",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Interest subsidy on education loans for overseas studies",
        "tags": ["Education Loan", "Minority Students", "Study Abroad"]
    },
    {
        "name": "Nai Manzil",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Education and skill development for minority youth without formal schooling",
        "tags": ["Skill Development", "Minority Youth", "Education"]
    },
    {
        "name": "USTTAD (Upgrading Skills & Training in Traditional Arts/Crafts for Development)",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Preserves traditional ancestral arts/crafts of minority communities",
        "tags": ["Traditional Arts", "Skill Training", "Minority Communities"]
    },
    {
        "name": "Seekho aur Kamao",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Skill development training for minority youth",
        "tags": ["Skill Development", "Minority Youth", "Employment"]
    },
    {
        "name": "Jiyo Parsi",
        "ministry": "Ministry Of Minority Affairs",
        "description": "Arrests declining population trend among Parsis",
        "tags": ["Parsi Community", "Population", "Welfare"]
    },
    {
        "name": "National Overseas Scholarship for SC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance for SC students pursuing Masters/Ph.D abroad",
        "tags": ["Scholarship", "SC Students", "Study Abroad"]
    },
    {
        "name": "Dr. Ambedkar Centrally Sponsored Scheme of Post-Matric Scholarship for EBC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance for economically backward class students",
        "tags": ["Scholarship", "EBC Students", "Higher Education"]
    },
    {
        "name": "Top Class Education for SC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Full financial support for SC students in notified institutions",
        "tags": ["Scholarship", "SC Students", "Quality Education"]
    },
    {
        "name": "National Fellowship for SC Students",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Fellowship for SC students pursuing M.Phil/Ph.D",
        "tags": ["Fellowship", "SC Students", "Research"]
    },
    {
        "name": "Babu Jagjivan Ram Chhatrawas Yojana",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Hostel facilities for SC boys and girls",
        "tags": ["Hostel", "SC Students", "Education"]
    },
    {
        "name": "National Safai Karamcharis Finance & Development Corporation",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to safai karamcharis for self-employment",
        "tags": ["Sanitation Workers", "Self Employment", "Finance"]
    },
    {
        "name": "Self Employment Scheme for Rehabilitation of Manual Scavengers (SRMS)",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Rehabilitates manual scavengers in alternative occupations",
        "tags": ["Manual Scavengers", "Rehabilitation", "Alternative Livelihood"]
    },
    {
        "name": "Stand Up India Scheme for SC/ST Entrepreneurs",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Bank loans for SC/ST entrepreneurs to set up greenfield enterprises",
        "tags": ["Entrepreneurship", "SC/ST", "Bank Loans"]
    },
    {
        "name": "Venture Capital Fund for SCs",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Concessional finance to SC entrepreneurs",
        "tags": ["Venture Capital", "SC Entrepreneurs", "Finance"]
    },
    {
        "name": "National Backward Classes Finance & Development Corporation",
        "ministry": "Ministry Of Social Justice and Empowerment",
        "description": "Financial assistance to backward classes for income generating activities",
        "tags": ["OBC", "Financial Assistance", "Livelihood"]
    },
    {
        "name": "National Handicapped Finance & Development Corporation",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Financial assistance to persons with disabilities for self-employment",
        "tags": ["Disabled Persons", "Self Employment", "Finance"]
    },
    {
        "name": "Assistance to Disabled Persons for Purchase/Fitting of Aids and Appliances (ADIP)",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Assistive devices to persons with disabilities",
        "tags": ["Disabled Persons", "Assistive Devices", "Rehabilitation"]
    },
    {
        "name": "Deendayal Disabled Rehabilitation Scheme",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Grants to NGOs for rehabilitation of persons with disabilities",
        "tags": ["Disabled Persons", "Rehabilitation", "NGO Support"]
    },
    {
        "name": "Accessible India Campaign (Sugamya Bharat Abhiyan)",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Universal accessibility for persons with disabilities",
        "tags": ["Accessibility", "Disabled Persons", "Infrastructure"]
    },
    {
        "name": "Unique Disability ID (UDID)",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "National database for persons with disabilities",
        "tags": ["Disabled Persons", "Database", "Identity"]
    },
    {
        "name": "National Trust Schemes",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Support to persons with autism, cerebral palsy, mental retardation and multiple disabilities",
        "tags": ["Disabled Persons", "Autism", "Cerebral Palsy", "Support Services"]
    },
    {
        "name": "Pre-Matric Scholarship for Students with Disabilities",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Financial assistance to disabled students in classes IX and X",
        "tags": ["Scholarship", "Disabled Students", "Education"]
    },
    {
        "name": "Post-Matric Scholarship for Students with Disabilities",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Financial assistance to disabled students for post-matriculation studies",
        "tags": ["Scholarship", "Disabled Students", "Higher Education"]
    },
    {
        "name": "National Fellowship for Students with Disabilities",
        "ministry": "Department Of Empowerment of Persons with Disabilities",
        "description": "Fellowship for disabled students pursuing M.Phil/Ph.D",
        "tags": ["Fellowship", "Disabled Students", "Research"]
    },
    {
        "name": "Pre-Matric Scholarship for ST Students",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Financial assistance to ST students studying in classes IX and X",
        "tags": ["Scholarship", "ST Students", "Education"]
    },
    {
        "name": "Post-Matric Scholarship for ST Students",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Financial assistance to ST students for post-matriculation studies",
        "tags": ["Scholarship", "ST Students", "Higher Education"]
    },
    {
        "name": "National Overseas Scholarship for ST Students",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Financial assistance for ST students pursuing Masters/Ph.D abroad",
        "tags": ["Scholarship", "ST Students", "Study Abroad"]
    },
    {
        "name": "National Fellowship for ST Students",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Fellowship for ST students pursuing M.Phil/Ph.D",
        "tags": ["Fellowship", "ST Students", "Research"]
    },
    {
        "name": "Rajiv Gandhi National Fellowship for ST Students",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Fellowship for ST students pursuing M.Phil/Ph.D",
        "tags": ["Fellowship", "ST Students", "Research"]
    },
    {
        "name": "National Scheduled Tribes Finance & Development Corporation",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Financial assistance to ST population for income generating activities",
        "tags": ["ST", "Financial Assistance", "Livelihood"]
    },
    {
        "name": "Eklavya Model Residential Schools",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Quality education to ST children in remote areas",
        "tags": ["ST Students", "Residential School", "Quality Education"]
    },
    {
        "name": "Van Dhan Vikas Kendra",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Value addition to minor forest produce through tribal self-help groups",
        "tags": ["Tribal Welfare", "Forest Produce", "Value Addition"]
    },
    {
        "name": "PM-JANMAN (Pradhan Mantri Janjati Adivasi Nyaya Maha Abhiyan)",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Socio-economic development of Particularly Vulnerable Tribal Groups",
        "tags": ["PVTG", "Tribal Development", "Infrastructure"]
    },
    {
        "name": "Scheme for Development of PVTGs",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Comprehensive development of Particularly Vulnerable Tribal Groups",
        "tags": ["PVTG", "Tribal Welfare", "Development"]
    },
    {
        "name": "Grants under Article 275(1) of Constitution",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Grants to states with scheduled areas for raising administration level",
        "tags": ["Tribal Areas", "State Grants", "Development"]
    },
    {
        "name": "Support to Tribal Research Institutes",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Strengthens tribal research institutes in states",
        "tags": ["Tribal Research", "Institutes", "Capacity Building"]
    },
    {
        "name": "Pradhan Mantri Adi Adarsh Gram Yojana",
        "ministry": "Ministry Of Tribal Affairs",
        "description": "Integrated development of tribal villages",
        "tags": ["Tribal Villages", "Integrated Development", "Infrastructure"]
    },
    {
        "name": "PM SVANIDHI (Street Vendors AtmaNirbhar Nidhi)",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Working capital loan for street vendors",
        "tags": ["Street Vendors", "Micro Credit", "Urban Livelihood"]
    },
    {
        "name": "Deendayal Antyodaya Yojana - National Urban Livelihoods Mission (DAY-NULM)",
        "ministry": "Ministry Of Housing and Urban Affairs",
        "description": "Skill development and self-employment for urban poor",
        "tags": ["Urban Poor", "Livelihood", "Skill Development"]
    },
    {
        "name": "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission (DAY-NRLM)",
        "ministry": "Ministry Of Rural Development",
        "description": "Mobilizes rural poor into self-help groups for livelihood opportunities",
        "tags": ["Rural Poor", "SHG", "Livelihood"]
    },
    {
        "name": "Deen Dayal Upadhyaya Grameen Kaushalya Yojana (DDU-GKY)",
        "ministry": "Ministry Of Rural Development",
        "description": "Placement linked skill development for rural youth",
        "tags": ["Rural Youth", "Skill Training", "Placement"]
    },
    {
        "name": "Shyama Prasad Mukherji Rurban Mission",
        "ministry": "Ministry Of Rural Development",
        "description": "Develops rural clusters with urban amenities",
        "tags": ["Rural Development", "Urban Amenities", "Cluster Development"]
    },
    {
        "name": "Pradhan Mantri Adarsh Gram Yojana",
        "ministry": "Ministry Of Rural Development",
        "description": "Integrated development of SC majority villages",
        "tags": ["SC Villages", "Integrated Development", "Rural Development"]
    },
    {
        "name": "National Rural Drinking Water Programme",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Provides adequate safe drinking water to rural population",
        "tags": ["Drinking Water", "Rural Areas", "Water Supply"]
    },
    {
        "name": "Swachh Bharat Mission - Gramin",
        "ministry": "Ministry Of Jal Shakti",
        "description": "Makes rural India open defecation free",
        "tags": ["Sanitation", "Rural Areas", "ODF"]
    },
    {
        "name": "National Rurban Mission",
        "ministry": "Ministry Of Rural Development",
        "description": "Develops smart villages with urban facilities",
        "tags": ["Smart Villages", "Rural Development", "Infrastructure"]
    },
    {
        "name": "SAGY (Saansad Adarsh Gram Yojana)",
        "ministry": "Ministry Of Rural Development",
        "description": "MPs adopt and develop model villages",
        "tags": ["Model Villages", "Rural Development", "MP Adoption"]
    },
    {
        "name": "Prime Minister's Development Package for Jammu & Kashmir",
        "ministry": "Prime Minister's Office",
        "description": "Infrastructure and employment generation in J&K",
        "tags": ["J&K", "Infrastructure", "Employment"]
    },
    {
        "name": "Special Package for North East Region",
        "ministry": "Ministry Of Development of North Eastern Region",
        "description": "Accelerated development of North East states",
        "tags": ["North East", "Development", "Infrastructure"]
    },
    {
        "name": "PM's Reconstruction Plan for Central Yemen",
        "ministry": "Ministry Of External Affairs",
        "description": "India's contribution to Yemen reconstruction",
        "tags": ["International", "Yemen", "Reconstruction"]
    },
    {
        "name": "Maitri Setu - India Bangladesh Friendship Bridge",
        "ministry": "Ministry Of External Affairs",
        "description": "Connectivity project between India and Bangladesh",
        "tags": ["Infrastructure", "Bangladesh", "Connectivity"]
    },
    {
        "name": "India-Myanmar-Thailand Trilateral Highway",
        "ministry": "Ministry Of External Affairs",
        "description": "Regional connectivity project",
        "tags": ["International", "Highway", "Connectivity"]
    },
    {
        "name": "Chabahar Port Development",
        "ministry": "Ministry Of External Affairs",
        "description": "Strategic port development in Iran for regional connectivity",
        "tags": ["Port", "Iran", "Connectivity"]
    },
    {
        "name": "International Solar Alliance",
        "ministry": "Ministry Of New and Renewable Energy",
        "description": "Coalition of solar resource rich countries",
        "tags": ["Solar Energy", "International", "Renewable Energy"]
    },
    {
        "name": "Coalition for Disaster Resilient Infrastructure (CDRI)",
        "ministry": "Prime Minister's Office",
        "description": "Global partnership for disaster resilient infrastructure",
        "tags": ["Disaster Management", "Infrastructure", "International"]
    },
    {
        "name": "Vande Bharat Mission",
        "ministry": "Ministry Of External Affairs",
        "description": "Repatriation of Indian nationals during COVID-19",
        "tags": ["Evacuation", "COVID-19", "Citizens Abroad"]
    },
    {
        "name": "Vaccine Maitri",
        "ministry": "Ministry Of External Affairs",
        "description": "India's vaccine diplomacy initiative",
        "tags": ["Vaccines", "International", "COVID-19"]
    },
    {
        "name": "Indian Technical and Economic Cooperation (ITEC)",
        "ministry": "Ministry Of External Affairs",
        "description": "Capacity building and training for developing countries",
        "tags": ["International", "Training", "Capacity Building"]
    },
    {
        "name": "Know India Programme",
        "ministry": "Ministry Of External Affairs",
        "description": "Familiarizes Indian diaspora youth with Indian culture and heritage",
        "tags": ["Diaspora", "Youth", "Culture"]
    },
    {
        "name": "Pravasi Bharatiya Divas",
        "ministry": "Ministry Of External Affairs",
        "description": "Annual event to connect with Indian diaspora",
        "tags": ["Diaspora", "Event", "NRI"]
    },
    {
        "name": "Overseas Citizenship of India (OCI)",
        "ministry": "Ministry Of External Affairs",
        "description": "Allows persons of Indian origin to live and work in India",
        "tags": ["Diaspora", "Citizenship", "NRI"]
    },
    {
        "name": "e-Vidya Bharti and e-Arogya Bharti",
        "ministry": "Ministry Of External Affairs",
        "description": "Tele-education and tele-medicine for developing countries",
        "tags": ["International", "Education", "Healthcare"]
    },
    {
        "name": "Passport Seva Kendra",
        "ministry": "Ministry Of External Affairs",
        "description": "Delivery of passport services through post office network",
        "tags": ["Passport", "Service Delivery", "Citizens"]
    },
    {
        "name": "Mission Karmayogi",
        "ministry": "Department Of Personnel and Training",
        "description": "Civil service capacity building programme",
        "tags": ["Civil Services", "Training", "Capacity Building"]
    },
    {
        "name": "Special Campaign for Disposal of Pending Matters",
        "ministry": "Department Of Administrative Reforms & Public Grievances",
        "description": "Disposal of pending references, PMO references, parliament assurances",
        "tags": ["Governance", "Disposal", "Efficiency"]
    },
    {
        "name": "Sevottam Model",
        "ministry": "Department Of Administrative Reforms & Public Grievances",
        "description": "Framework for improving service delivery in public services",
        "tags": ["Service Delivery", "Quality", "Governance"]
    },
    {
        "name": "PM's Awards for Excellence in Public Administration",
        "ministry": "Department Of Administrative Reforms & Public Grievances",
        "description": "Recognizes excellence in public administration",
        "tags": ["Awards", "Public Administration", "Excellence"]
    },
    {
        "name": "Good Governance Index",
        "ministry": "Department Of Administrative Reforms & Public Grievances",
        "description": "Measures governance performance across states",
        "tags": ["Governance", "Index", "Performance"]
    },
    {
        "name": "Centralized Public Grievance Redress and Monitoring System (CPGRAMS)",
        "ministry": "Department Of Administrative Reforms & Public Grievances",
        "description": "Online platform for lodging and tracking grievances",
        "tags": ["Grievance Redressal", "e-Governance", "Citizens"]
    },
    {
        "name": "MyGov Platform",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Citizen engagement platform for participatory governance",
        "tags": ["Citizen Engagement", "e-Governance", "Participation"]
    },
    {
        "name": "Umang App",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Unified mobile application for accessing government services",
        "tags": ["Mobile App", "e-Governance", "Service Delivery"]
    },
    {
        "name": "DigiLocker",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Digital storage for government issued documents",
        "tags": ["Digital Documents", "Cloud Storage", "e-Governance"]
    },
    {
        "name": "e-Hospital",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Digital platform for hospital management",
        "tags": ["Healthcare", "Digital", "Hospital Management"]
    },
    {
        "name": "e-Sanjeevani",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "National telemedicine service",
        "tags": ["Telemedicine", "Healthcare", "Digital Health"]
    },
    {
        "name": "Co-WIN Platform",
        "ministry": "Ministry Of Health & Family Welfare",
        "description": "Digital platform for COVID-19 vaccination management",
        "tags": ["COVID-19", "Vaccination", "Digital Platform"]
    },
    {
        "name": "Aarogya Setu App",
        "ministry": "Ministry Of Electronics and Information Technology",
        "description": "Contact tracing app for COVID-19",
        "tags": ["COVID-19", "Contact Tracing", "Mobile App"]
    },
    {
        "name": "e-Courts Mission Mode Project",
        "ministry": "Department Of Justice",
        "description": "ICT enablement of courts for efficient case management",
        "tags": ["Judiciary", "Digital", "Case Management"]
    },
    {
        "name": "e-Filing of Cases",
        "ministry": "Department Of Justice",
        "description": "Electronic filing of cases in courts",
        "tags": ["Judiciary", "e-Filing", "Digital"]
    },
    {
        "name": "Video Conferencing in Courts",
        "ministry": "Department Of Justice",
        "description": "Virtual court hearings through video conference",
        "tags": ["Judiciary", "Video Conference", "Digital Courts"]
    },
    {
        "name": "Tele Law",
        "ministry": "Department Of Justice",
        "description": "Provides legal advice through video conferencing at Common Service Centres",
        "tags": ["Legal Services", "Telemedicine", "Access to Justice"]
    },
    {
        "name": "NALSA (National Legal Services Authority)",
        "ministry": "Department Of Justice",
        "description": "Free legal services to marginalized sections",
        "tags": ["Legal Aid", "Access to Justice", "Marginalized"]
    },
    {
        "name": "Nyaya Bandhu - Pro Bono Legal Services",
        "ministry": "Department Of Justice",
        "description": "Connects law students with legal aid seekers",
        "tags": ["Legal Aid", "Pro Bono", "Law Students"]
    },
    {
        "name": "Fast Track Special Courts",
        "ministry": "Department Of Justice",
        "description": "Expeditious trial of rape and POCSO cases",
        "tags": ["Judiciary", "Fast Track", "Women and Child Protection"]
    },
    {
        "name": "National Mission for Justice Delivery and Legal Reforms",
        "ministry": "Department Of Justice",
        "description": "Reforms for reducing delays and arrears in judicial system",
        "tags": ["Judicial Reforms", "Case Disposal", "Access to Justice"]
    },
    {
        "name": "e-Prosecution",
        "ministry": "Department Of Justice",
        "description": "Digital system for prosecution management",
        "tags": ["Prosecution", "Digital", "Case Management"]
    },
    {
        "name": "Interoperable Criminal Justice System (ICJS)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Integration of police, courts, prisons and forensic systems",
        "tags": ["Criminal Justice", "Integration", "Digital"]
    },
    {
        "name": "Crime and Criminal Tracking Network & Systems (CCTNS)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Comprehensive IT solution for police stations",
        "tags": ["Police", "Crime Tracking", "Digital"]
    },
    {
        "name": "Emergency Response Support System (ERSS)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Single emergency number 112 for all emergencies",
        "tags": ["Emergency", "Police", "Citizen Safety"]
    },
    {
        "name": "National Database on Sexual Offenders (NDSO)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Database of convicted sexual offenders",
        "tags": ["Sexual Offenders", "Database", "Law Enforcement"]
    },
    {
        "name": "National Cyber Crime Reporting Portal",
        "ministry": "Ministry Of Home Affairs",
        "description": "Online platform for reporting cybercrimes",
        "tags": ["Cybercrime", "Reporting", "Digital"]
    },
    {
        "name": "Indian Cyber Crime Coordination Centre (I4C)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Nodal point for combating cybercrime",
        "tags": ["Cybercrime", "Coordination", "Law Enforcement"]
    },
    {
        "name": "National Intelligence Grid (NATGRID)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Counter-terrorism intelligence sharing platform",
        "tags": ["Intelligence", "Counter-Terrorism", "Security"]
    },
    {
        "name": "Nirbhaya Fund Projects",
        "ministry": "Ministry Of Home Affairs",
        "description": "Safety and security of women",
        "tags": ["Women Safety", "Security", "Infrastructure"]
    },
    {
        "name": "Safe City Projects",
        "ministry": "Ministry Of Home Affairs",
        "description": "CCTV surveillance and security infrastructure in cities",
        "tags": ["Urban Safety", "Surveillance", "Women Security"]
    },
    {
        "name": "Modernization of Police Force",
        "ministry": "Ministry Of Home Affairs",
        "description": "Upgrades infrastructure, equipment and technology for police",
        "tags": ["Police", "Modernization", "Infrastructure"]
    },
    {
        "name": "National Disaster Response Force (NDRF)",
        "ministry": "Ministry Of Home Affairs",
        "description": "Specialized force for disaster response",
        "tags": ["Disaster Management", "Emergency Response", "Rescue"]
    },
    {
        "name": "National Disaster Management Plan",
        "ministry": "Ministry Of Home Affairs",
        "description": "Framework for disaster management in India",
        "tags": ["Disaster Management", "Planning", "Preparedness"]
    },
    {
        "name": "Aadhaar",
        "ministry": "Unique Identification Authority of India",
        "description": "12-digit unique identity number for Indian residents",
        "tags": ["Identity", "Aadhaar", "Biometric"]
    },
    {
        "name": "e-KYC Services",
        "ministry": "Unique Identification Authority of India",
        "description": "Electronic Know Your Customer using Aadhaar",
        "tags": ["KYC", "Aadhaar", "Digital Verification"]
    },
    {
        "name": "Aadhaar Enabled Payment System (AEPS)",
        "ministry": "Unique Identification Authority of India",
        "description": "Bank transactions using Aadhaar authentication",
        "tags": ["Banking", "Aadhaar", "Digital Payments"]
    },
    {
        "name": "Direct Benefit Transfer (DBT)",
        "ministry": "Ministry Of Finance",
        "description": "Direct transfer of subsidies to beneficiary accounts using Aadhaar",
        "tags": ["Subsidy", "DBT", "Financial Inclusion"]
    },
    {
        "name": "BHIM (Bharat Interface for Money)",
        "ministry": "Ministry Of Finance",
        "description": "Mobile app for digital payments using UPI",
        "tags": ["Digital Payments", "UPI", "Mobile App"]
    },
    {
        "name": "UPI (Unified Payments Interface)",
        "ministry": "Ministry Of Finance",
        "description": "Instant real-time payment system",
        "tags": ["Digital Payments", "UPI", "Banking"]
    },
    {
        "name": "RuPay Card",
        "ministry": "Ministry Of Finance",
        "description": "Domestic card payment network",
        "tags": ["Payment Cards", "Digital Payments", "Banking"]
    },
    {
        "name": "National Pension System (NPS)",
        "ministry": "Ministry Of Finance",
        "description": "Pension scheme for retirement savings",
        "tags": ["Pension", "Retirement", "Savings"]
    },
    {
        "name": "APY (Atal Pension Yojana)",
        "ministry": "Ministry Of Finance",
        "description": "Guaranteed pension for unorganized sector workers",
        "tags": ["Pension", "Social Security", "Unorganized Sector"]
    },
    {
        "name": "PM CARES for Children",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Support for children orphaned due to COVID-19",
        "tags": ["COVID-19", "Orphans", "Child Welfare"]
    },
    {
        "name": "Vatsalya - Mission Vatsalya",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Secure childhood for vulnerable children",
        "tags": ["Child Protection", "Vulnerable Children", "Welfare"]
    },
    {
        "name": "Mission Saksham Anganwadi and Poshan 2.0",
        "ministry": "Ministry Of Women & Child Development",
        "description": "Strengthens nutritional content delivery and outreach",
        "tags": ["Nutrition", "Anganwadi", "Child Development"]
    }
]

# Helper function to get all scheme names for filtering
def get_scheme_names():
    """Returns list of all scheme names for keyword matching"""
    return [scheme["name"] for scheme in CENTRAL_SCHEMES]

# Helper function to get all scheme names including regional language variations
@lru_cache(maxsize=1)
def get_all_scheme_variations():
    """Returns dict with all scheme names and their regional variations for comprehensive matching"""
    variations = {}
    for scheme in CENTRAL_SCHEMES:
        # Add English name
        eng_name = scheme["name"]
        variations[eng_name.lower()] = scheme
        
        # Add all regional language variations
        if "regional_names" in scheme:
            for lang, names in scheme["regional_names"].items():
                for regional_name in names:
                    variations[regional_name.lower()] = scheme
    
    return variations

# Helper function to match scheme in text (works for all languages)
def find_schemes_in_text(text: str, detected_language: str = None):
    """
    Find all schemes mentioned in text (supports all Indian languages)
    Returns list of matched scheme objects
    """
    if not text:
        return []
    
    text_lower = text.lower()
    matched_schemes = []
    seen = set()
    
    for scheme in CENTRAL_SCHEMES:
        # Check English name
        if scheme["name"].lower() in text_lower:
            if scheme["name"] not in seen:
                matched_schemes.append(scheme)
                seen.add(scheme["name"])
            continue
        
        # Check words from English name (for partial matches like "KISAN" from "PM-KISAN")
        name_words = [w for w in scheme["name"].lower().split() if len(w) > 4]
        if any(word in text_lower for word in name_words):
            if scheme["name"] not in seen:
                matched_schemes.append(scheme)
                seen.add(scheme["name"])
            continue
        
        # Check regional language variations
        if "regional_names" in scheme:
            # If language detected, prioritize that language
            if detected_language and detected_language in scheme["regional_names"]:
                for regional_name in scheme["regional_names"][detected_language]:
                    if regional_name.lower() in text_lower:
                        if scheme["name"] not in seen:
                            matched_schemes.append(scheme)
                            seen.add(scheme["name"])
                        break
            
            # Also check all other regional names
            for lang, names in scheme["regional_names"].items():
                for regional_name in names:
                    if regional_name.lower() in text_lower:
                        if scheme["name"] not in seen:
                            matched_schemes.append(scheme)
                            seen.add(scheme["name"])
                        break
    
    return matched_schemes

# Helper function to get scheme by name
def get_scheme_by_name(name):
    """Returns scheme details by name"""
    for scheme in CENTRAL_SCHEMES:
        if name.lower() in scheme["name"].lower():
            return scheme
    return None

# Helper function to search schemes by ministry
def get_schemes_by_ministry(ministry):
    """Returns all schemes under a ministry"""
    return [scheme for scheme in CENTRAL_SCHEMES if ministry.lower() in scheme["ministry"].lower()]

# Helper function to search schemes by tag
def get_schemes_by_tag(tag):
    """Returns all schemes with a specific tag"""
    return [scheme for scheme in CENTRAL_SCHEMES if tag.lower() in [t.lower() for t in scheme["tags"]]]
