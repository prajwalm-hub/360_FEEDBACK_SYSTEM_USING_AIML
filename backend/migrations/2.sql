
INSERT INTO categories (name, description, color) VALUES
('Health', 'Health and medical news', '#3b82f6'),
('Education', 'Educational policies and news', '#10b981'),
('Policy', 'Government policies and announcements', '#8b5cf6'),
('Governance', 'Administrative and governance updates', '#f59e0b'),
('Economy', 'Economic news and financial updates', '#ef4444'),
('Technology', 'Technology and digital initiatives', '#06b6d4'),
('Environment', 'Environmental and climate news', '#84cc16');

INSERT INTO news_articles (
  title, content, summary, original_language, translated_title, translated_content,
  source_url, source_name, published_at, category, sentiment_score, sentiment_label,
  region, tags, is_processed
) VALUES
('स्वास्थ्य मंत्रालय ने नई योजना की घोषणा की', 'स्वास्थ्य मंत्रालय ने ग्रामीण क्षेत्रों में बेहतर स्वास्थ्य सेवाओं के लिए एक नई योजना की घोषणा की है। इस योजना के तहत 1000 नए प्राथमिक स्वास्थ्य केंद्र स्थापित किए जाएंगे।', 'Health Ministry announces new scheme for rural healthcare with 1000 new primary health centers.', 'hindi', 'Health Ministry announces new scheme', 'The Health Ministry has announced a new scheme for better healthcare services in rural areas. Under this scheme, 1000 new primary health centers will be established.', 'https://example.com/news1', 'Dainik Jagran', '2025-09-29 10:30:00', 'Health', 0.8, 'positive', 'North India', 'healthcare,rural,government', 1),

('शिक्षा क्षेत्र में डिजिटल पहल', 'सरकार ने डिजिटल शिक्षा को बढ़ावा देने के लिए नई नीति का अनावरण किया है। इसके तहत सभी सरकारी स्कूलों में टैबलेट वितरित किए जाएंगे।', 'Government unveils new digital education policy with tablet distribution in government schools.', 'hindi', 'Digital initiative in education sector', 'The government has unveiled a new policy to promote digital education. Under this, tablets will be distributed to all government schools.', 'https://example.com/news2', 'Hindustan Times', '2025-09-29 09:15:00', 'Education', 0.7, 'positive', 'Central India', 'education,digital,tablets', 1),

('তথ্য প্রযুক্তি খাতে নতুন বিনিয়োগ', 'পশ্চিমবঙ্গ সরকার তথ্য প্রযুক্তি খাতে ৫০০ করোড় টাকা বিনিয়োগের ঘোষণা দিয়েছে। এই উদ্যোগে হাজার হাজার নতুন চাকরির সুযোগ সৃষ্টি হবে।', 'West Bengal government announces 500 crore investment in IT sector creating thousands of jobs.', 'bengali', 'New investment in information technology sector', 'The West Bengal government has announced an investment of 500 crores in the information technology sector. This initiative will create thousands of new job opportunities.', 'https://example.com/news3', 'Anandabazar Patrika', '2025-09-29 11:45:00', 'Technology', 0.9, 'positive', 'East India', 'technology,investment,jobs', 1),

('पर्यावरण संरक्षण के लिए नए नियम', 'महाराष्ट्र सरकार ने पर्यावरण संरक्षण के लिए कड़े नियमों की घोषणा की है। प्लास्टिक के उपयोग पर पूर्ण प्रतिबंध लगाया जाएगा।', 'Maharashtra government announces strict environmental protection rules with complete plastic ban.', 'marathi', 'New rules for environmental protection', 'The Maharashtra government has announced strict rules for environmental protection. A complete ban on plastic use will be imposed.', 'https://example.com/news4', 'Maharashtra Times', '2025-09-29 08:20:00', 'Environment', 0.6, 'positive', 'West India', 'environment,plastic,ban', 1),

('தமிழ்நாட்டில் புதிய மருத்துவக் கல்லூரி', 'தமிழ்நாடு அரசு மூன்று புதிய மருத்துவக் கல்லூரிகளை அறிவித்துள்ளது. இது மாநிலத்தில் மருத்துவ கல்வியை மேம்படுத்தும்.', 'Tamil Nadu government announces three new medical colleges to improve medical education in the state.', 'tamil', 'New medical college in Tamil Nadu', 'The Tamil Nadu government has announced three new medical colleges. This will improve medical education in the state.', 'https://example.com/news5', 'The Hindu Tamil', '2025-09-29 12:30:00', 'Education', 0.8, 'positive', 'South India', 'medical,education,college', 1),

('ఆర్థిక రంగంలో కొత్త సంస్కరణలు', 'తెలంగాణ ప్రభుత్వం ఆర్థిక రంగంలో కొత్త సంస్కరణలను ప్రకటించింది. చిన్న వ్యాపారులకు రుణాలు సులభంగా అందుబాటులోకి వస్తాయి।', 'Telangana government announces new economic reforms making loans easily accessible to small businesses.', 'telugu', 'New reforms in economic sector', 'The Telangana government has announced new reforms in the economic sector. Loans will be easily accessible to small businesses.', 'https://example.com/news6', 'Eenadu', '2025-09-29 14:15:00', 'Economy', 0.7, 'positive', 'South India', 'economy,reforms,loans', 1),

('गुजरात में सौर ऊर्जा परियोजना', 'गुजरात सरकार ने राज्य में सबसे बड़ी सौर ऊर्जा परियोजना की शुरुआत की है। यह परियोजना 10 लाख घरों को बिजली प्रदान करेगी।', 'Gujarat government launches state''s largest solar energy project to power 10 lakh homes.', 'gujarati', 'Solar energy project in Gujarat', 'The Gujarat government has launched the largest solar energy project in the state. This project will provide electricity to 10 lakh homes.', 'https://example.com/news7', 'Gujarat Samachar', '2025-09-29 13:00:00', 'Environment', 0.9, 'positive', 'West India', 'solar,energy,renewable', 1),

('कर्नाटक में कृषि नीति में बदलाव', 'कर्नाटक सरकार ने किसानों के लिए नई कृषि नीति की घोषणा की है। इसमें फसल बीमा और न्यूनतम समर्थन मूल्य में वृद्धि शामिल है।', 'Karnataka government announces new agricultural policy with crop insurance and increased MSP for farmers.', 'kannada', 'Changes in agricultural policy in Karnataka', 'The Karnataka government has announced a new agricultural policy for farmers. This includes crop insurance and increase in minimum support price.', 'https://example.com/news8', 'Vijaya Karnataka', '2025-09-29 15:45:00', 'Policy', 0.8, 'positive', 'South India', 'agriculture,farmers,policy', 1);
