CREATE TABLE @table (
  path  TEXT NOT NULL PRIMARY KEY,
  crawled BOOL,
  stored BOOL,
  crawled_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
