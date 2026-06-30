const ADMIN_PAGE_IDS = new Set([
  "upload",
  "qa",
  "gen",
  "analytics",
  "settings",
]);

export function canAccessPage(pageId, role) {
  return role === "admin" || !ADMIN_PAGE_IDS.has(pageId);
}

export function filterNavigationItems(items, role) {
  return items.filter((item) => canAccessPage(item.id, role));
}

