/**
 * Resolves uploaded media URLs to absolute URLs in production while preserving
 * relative proxy paths in local development.
 */
export const resolveImageUrl = (url) => {
  if (!url) return null;
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) {
    return url;
  }
  const apiBase = import.meta.env.VITE_API_BASE_URL || (import.meta.env.PROD ? "https://eventx-backend-b6zs.onrender.com/api" : "/api");
  if (apiBase.startsWith("http://") || apiBase.startsWith("https://")) {
    try {
      const origin = new URL(apiBase).origin;
      return `${origin}${url.startsWith("/") ? "" : "/"}${url}`;
    } catch {
      return url;
    }
  }
  return url;
};
