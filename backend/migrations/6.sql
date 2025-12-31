
-- Insert sample news articles with diverse content
INSERT INTO news_articles (
    title, content, summary, original_language, translated_title, translated_content,
    source_url, source_name, published_at, category, sentiment_score, sentiment_label,
    region, tags, is_processed, created_at, updated_at
) VALUES 
-- Health articles
('नई स्वास्थ्य योजना शुरू', 'सरकार ने गरीब परिवारों के लिए नई स्वास्थ्य योजना की घोषणा की है।', 'Government announces new health scheme for poor families', 'hindi', 'New Health Scheme Launched', 'Government has announced a new health scheme for poor families.', 'https://example.com/news1', 'Dainik Jagran', '2024-09-28 10:00:00', 'Health', 0.7, 'positive', 'North India', 'health,scheme,government', 1, datetime('now', '-1 day'), datetime('now', '-1 day')),

('Kerala improves healthcare infrastructure', 'Kerala government allocates additional budget for healthcare infrastructure development across rural areas.', 'Kerala allocates more budget for rural healthcare', 'english', null, null, 'https://example.com/news2', 'The Hindu', '2024-09-28 12:00:00', 'Health', 0.6, 'positive', 'South India', 'kerala,healthcare,infrastructure', 1, datetime('now', '-1 day'), datetime('now', '-1 day')),

-- Education articles  
('শিক্ষা ব্যবস্থায় নতুন সংস্কার', 'পশ্চিমবঙ্গে শিক্ষা ব্যবস্থায় নতুন সংস্কারের ঘোষণা করা হয়েছে।', 'New education reforms announced in West Bengal', 'bengali', 'New Education System Reforms', 'New education system reforms have been announced in West Bengal.', 'https://example.com/news3', 'Anandabazar Patrika', '2024-09-27 15:30:00', 'Education', 0.5, 'positive', 'East India', 'education,reform,bengal', 1, datetime('now', '-2 days'), datetime('now', '-2 days')),

('Digital classroom initiative fails to deliver', 'Several states report poor implementation of digital classroom programs with inadequate infrastructure.', 'Digital classroom programs face implementation challenges', 'english', null, null, 'https://example.com/news4', 'Indian Express', '2024-09-27 09:15:00', 'Education', -0.6, 'negative', 'Central India', 'digital,classroom,failure', 1, datetime('now', '-2 days'), datetime('now', '-2 days')),

-- Policy articles
('કૃષિ કાયદામાં સુધારો', 'ગુજરાત સરકારે કૃષિ ક્ષેત્રે નવા કાયદાની જાહેરાત કરી છે।', 'Gujarat announces new agricultural policy', 'gujarati', 'Agricultural Law Improvements', 'Gujarat government has announced new law in agriculture sector.', 'https://example.com/news5', 'Gujarat Samachar', '2024-09-26 14:20:00', 'Policy', 0.4, 'neutral', 'West India', 'agriculture,policy,gujarat', 1, datetime('now', '-3 days'), datetime('now', '-3 days')),

('Government policy on environment criticized', 'Environmental activists criticize new industrial policy for lack of environmental protection measures.', 'New industrial policy faces environmental criticism', 'english', null, null, 'https://example.com/news6', 'Times of India', '2024-09-26 11:45:00', 'Environment', -0.8, 'negative', 'Central India', 'environment,policy,criticism', 1, datetime('now', '-3 days'), datetime('now', '-3 days')),

-- Economy articles
('ਆਰਥਿਕ ਨੀਤੀ ਵਿੱਚ ਸੁਧਾਰ', 'ਪੰਜਾਬ ਸਰਕਾਰ ਨੇ ਨਵੀਂ ਆਰਥਿਕ ਨੀਤੀ ਦਾ ਐਲਾਨ ਕੀਤਾ ਹੈ।', 'Punjab announces new economic policy', 'punjabi', 'Economic Policy Improvements', 'Punjab government has announced new economic policy.', 'https://example.com/news7', 'Punjabi Tribune', '2024-09-25 16:10:00', 'Economy', 0.3, 'neutral', 'North India', 'economy,policy,punjab', 1, datetime('now', '-4 days'), datetime('now', '-4 days')),

-- Technology articles
('तमिळनाडु में डिजिटल क्रांति', 'तमिलनाडु सरकार ने राज्य में डिजिटल इंफ्रास्ट्रक्चर के विकास की योजना बनाई है।', 'Tamil Nadu plans digital infrastructure development', 'hindi', 'Digital Revolution in Tamil Nadu', 'Tamil Nadu government has planned digital infrastructure development in the state.', 'https://example.com/news8', 'Dainik Bhaskar', '2024-09-25 13:25:00', 'Technology', 0.8, 'positive', 'South India', 'technology,digital,tamil nadu', 1, datetime('now', '-4 days'), datetime('now', '-4 days')),

-- Governance articles
('మహారాష్ట్రలో పరిపాలనా సంస్కరణలు', 'మహారాష్ట్ర ప్రభుత్వం కొత్త పరిపాలనా సంస్కరణలను ప్రకటించింది।', 'Maharashtra announces administrative reforms', 'telugu', 'Administrative Reforms in Maharashtra', 'Maharashtra government has announced new administrative reforms.', 'https://example.com/news9', 'Eenadu', '2024-09-24 10:40:00', 'Governance', 0.2, 'neutral', 'West India', 'governance,reform,maharashtra', 1, datetime('now', '-5 days'), datetime('now', '-5 days')),

('Corruption scandal rocks state government', 'Major corruption scandal emerges involving high-ranking government officials in infrastructure projects.', 'Government corruption scandal in infrastructure exposed', 'english', null, null, 'https://example.com/news10', 'The Wire', '2024-09-24 08:15:00', 'Governance', -0.9, 'negative', 'North India', 'corruption,scandal,government', 1, datetime('now', '-5 days'), datetime('now', '-5 days')),

-- Recent articles for variety
('कर्नाटक में पर्यावरण संरक्षण', 'कर्नाटक सरकार ने वन संरक्षण के लिए नई पहल शुरू की है।', 'Karnataka starts new forest conservation initiative', 'hindi', 'Environmental Protection in Karnataka', 'Karnataka government has started new initiative for forest conservation.', 'https://example.com/news11', 'Prajavani', datetime('now', '-6 hours'), 'Environment', 0.7, 'positive', 'South India', 'environment,forest,karnataka', 1, datetime('now', '-6 hours'), datetime('now', '-6 hours')),

('ମଧ୍ୟ ପ୍ରଦେଶରେ ନୂତନ ଶିକ୍ଷା ଯୋଜନା', 'ମଧ୍ୟ ପ୍ରଦେଶ ସରକାର ନୂତନ ଶିକ୍ଷା ଯୋଜନା ଆରମ୍ଭ କରିଛନ୍ତି।', 'Madhya Pradesh launches new education scheme', 'odia', 'New Education Scheme in Madhya Pradesh', 'Madhya Pradesh government has launched new education scheme.', 'https://example.com/news12', 'Sambad', datetime('now', '-3 hours'), 'Education', 0.6, 'positive', 'Central India', 'education,scheme,madhya pradesh', 1, datetime('now', '-3 hours'), datetime('now', '-3 hours')),

('असम में स्वास्थ्य सेवा संकट', 'असम के ग्रामीण क्षेत्रों में स्वास्थ्य सेवाओं की कमी से समस्या बढ़ रही है।', 'Healthcare crisis in rural Assam areas', 'hindi', 'Healthcare Crisis in Assam', 'Problems increasing due to lack of healthcare services in rural areas of Assam.', 'https://example.com/news13', 'Amar Asom', datetime('now', '-2 hours'), 'Health', -0.7, 'negative', 'Northeast India', 'healthcare,crisis,assam', 1, datetime('now', '-2 hours'), datetime('now', '-2 hours')),

('Rajasthan tourism boost announced', 'Rajasthan government announces new tourism development projects to boost state economy.', 'New tourism projects to boost Rajasthan economy', 'english', null, null, 'https://example.com/news14', 'Rajasthan Patrika', datetime('now', '-1 hour'), 'Economy', 0.8, 'positive', 'North India', 'tourism,economy,rajasthan', 1, datetime('now', '-1 hour'), datetime('now', '-1 hour')),

('झारखंड में खनन नीति विवाद', 'झारखंड की नई खनन नीति को लेकर स्थानीय समुदायों में विरोध प्रदर्शन हो रहे हैं।', 'Mining policy protests in Jharkhand communities', 'hindi', 'Mining Policy Controversy in Jharkhand', 'Local communities are protesting against Jharkhand new mining policy.', 'https://example.com/news15', 'Prabhat Khabar', datetime('now', '-30 minutes'), 'Policy', -0.5, 'negative', 'East India', 'mining,policy,jharkhand,protest', 1, datetime('now', '-30 minutes'), datetime('now', '-30 minutes'));
