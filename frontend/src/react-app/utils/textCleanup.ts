export function cleanHtmlText(text: string | null | undefined): string {
  if (!text) return '';
  return text
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, ' ')
    .replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
}

export function sanitizeArticle(article: any) {
  return {
    ...article,
    title: cleanHtmlText(article.title),
    summary: cleanHtmlText(article.summary),
    content: cleanHtmlText(article.content),
    translated_title: cleanHtmlText(article.translated_title),
    translated_summary: cleanHtmlText(article.translated_summary),
  };
}

export function formatLastUpdated(date: Date): string {
  const diff = Date.now() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleString();
}
