
DELETE FROM alert_recipients WHERE alert_id IN (
  SELECT id FROM alerts WHERE article_id IN (1, 2, 3, 4)
);
DELETE FROM alerts WHERE article_id IN (1, 2, 3, 4);
