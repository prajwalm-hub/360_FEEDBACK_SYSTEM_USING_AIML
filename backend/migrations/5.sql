
-- Insert sample alerts to demonstrate the system
INSERT INTO alerts (
  article_id, alert_type, severity, title, description, sentiment_score, 
  is_read, is_sent, sent_at, created_at, updated_at
) VALUES
(1, 'negative_sentiment', 'high', 'Negative Coverage Alert: Governance', 'High negative sentiment detected (-0.92) in government-related news article: "[Translated] सरकारी योजना में देरी से नागरिक परेशान"', -0.92, 0, 1, datetime('now', '-2 hours'), datetime('now', '-2 hours'), datetime('now', '-2 hours')),
(2, 'negative_sentiment', 'medium', 'Negative Coverage Alert: Health', 'High negative sentiment detected (-0.85) in government-related news article: "[Translated] স্বাস্থ্য বিভাগের নতুন নীতি নিয়ে বিতর্ক"', -0.85, 0, 1, datetime('now', '-1 hour'), datetime('now', '-1 hour'), datetime('now', '-1 hour')),
(3, 'negative_sentiment', 'high', 'Negative Coverage Alert: Policy', 'High negative sentiment detected (-0.94) in government-related news article: "[Translated] नई शिक्षा नीति के विरोध में प्रदर्शन"', -0.94, 1, 1, datetime('now', '-3 hours'), datetime('now', '-3 hours'), datetime('now', '-3 hours')),
(4, 'negative_sentiment', 'medium', 'Negative Coverage Alert: Economy', 'High negative sentiment detected (-0.87) in government-related news article: "[Translated] आर्थिक सुधारों पर सवाल"', -0.87, 0, 1, datetime('now', '-30 minutes'), datetime('now', '-30 minutes'), datetime('now', '-30 minutes'));

-- Insert alert recipients for the sample alerts
INSERT INTO alert_recipients (alert_id, pib_officer_id, notification_method, is_delivered, delivered_at, created_at, updated_at) 
SELECT 
  a.id as alert_id,
  p.id as pib_officer_id,
  'email' as notification_method,
  1 as is_delivered,
  a.sent_at as delivered_at,
  a.created_at,
  a.updated_at
FROM alerts a
CROSS JOIN pib_officers p
WHERE a.id IN (1, 2, 3, 4) AND p.is_active = 1;
