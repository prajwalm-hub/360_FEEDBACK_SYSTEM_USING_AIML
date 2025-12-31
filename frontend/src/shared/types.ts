import z from "zod";

// Align frontend types with backend ArticleOut schema
export const NewsArticleSchema = z.object({
  id: z.string(),
  url: z.string(),
  title: z.string(),
  summary: z.string().nullable().optional(),
  content: z.string().nullable().optional(),
  source: z.string().nullable().optional(),
  region: z.string().nullable().optional(),
  language: z.string().nullable().optional(),
  detected_language: z.string().nullable().optional(),
  detected_script: z.string().nullable().optional(),
  language_confidence: z.number().nullable().optional(),
  translated_title: z.string().nullable().optional(),
  translated_summary: z.string().nullable().optional(),
  published_at: z.string().nullable().optional(),
  collected_at: z.string().nullable().optional(),
  sentiment_label: z.string().nullable().optional(),
  sentiment_score: z.number().nullable().optional(),
  topic_labels: z.array(z.string()).nullable().optional(),
  // Entities are loosely typed; allow any shape used by backend
  entities: z.any().nullable().optional(),
  // Optional GoI metadata
  is_goi: z.boolean().nullable().optional(),
  relevance_score: z.number().nullable().optional(),
  goi_ministries: z.array(z.string()).nullable().optional(),
  goi_schemes: z.array(z.string()).nullable().optional(),
  goi_matched_terms: z.array(z.string()).nullable().optional(),
  // Content classification
  content_category: z.string().nullable().optional(),
  content_sub_category: z.string().nullable().optional(),
  classification_confidence: z.number().nullable().optional(),
  classification_keywords: z.array(z.string()).nullable().optional(),
  should_show_pib: z.boolean().nullable().optional(),
  filter_reason: z.string().nullable().optional(),
});

export type NewsArticle = z.infer<typeof NewsArticleSchema>;

export const CategorySchema = z.object({
  id: z.number(),
  name: z.string(),
  description: z.string().nullable(),
  color: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type Category = z.infer<typeof CategorySchema>;

export const SentimentAnalyticsSchema = z.object({
  id: z.number(),
  article_id: z.number(),
  positive_score: z.number(),
  negative_score: z.number(),
  neutral_score: z.number(),
  overall_sentiment: z.string().nullable(),
  confidence_score: z.number(),
  keywords: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type SentimentAnalytics = z.infer<typeof SentimentAnalyticsSchema>;

export const NewsFilterSchema = z.object({
  category: z.string().optional(),
  sentiment: z.string().optional(),
  language: z.string().optional(),
  region: z.string().optional(),
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  search: z.string().optional(),
});

export type NewsFilter = z.infer<typeof NewsFilterSchema>;

export const DashboardStatsSchema = z.object({
  totalArticles: z.number(),
  todayArticles: z.number(),
  averageSentiment: z.number(),
  topCategories: z.array(z.object({
    category: z.string(),
    count: z.number(),
  })),
  languageDistribution: z.array(z.object({
    language: z.string(),
    count: z.number(),
  })),
  sentimentTrends: z.array(z.object({
    date: z.string(),
    positive: z.number(),
    negative: z.number(),
    neutral: z.number(),
  })),
  totalChangePercent: z.number().nullable().optional(),
  todayChangePercent: z.number().nullable().optional(),
});

export type DashboardStats = z.infer<typeof DashboardStatsSchema>;

export const PIBOfficerSchema = z.object({
  id: z.number(),
  name: z.string(),
  email: z.string(),
  phone: z.string().nullable(),
  department: z.string().nullable(),
  is_active: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type PIBOfficer = z.infer<typeof PIBOfficerSchema>;

export const AlertSchema = z.object({
  id: z.number(),
  article_id: z.number(),
  alert_type: z.string(),
  severity: z.string(),
  title: z.string(),
  description: z.string(),
  sentiment_score: z.number(),
  is_read: z.number(),
  is_sent: z.number(),
  sent_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type Alert = z.infer<typeof AlertSchema>;

export const AlertRecipientSchema = z.object({
  id: z.number(),
  alert_id: z.number(),
  pib_officer_id: z.number(),
  notification_method: z.string(),
  is_delivered: z.number(),
  delivered_at: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type AlertRecipient = z.infer<typeof AlertRecipientSchema>;
