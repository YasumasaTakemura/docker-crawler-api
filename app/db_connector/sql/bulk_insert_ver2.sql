INSERT INTO @table (
  path,
  crawled,
  stored,
  crawled_at,
  created_at,
  updated_at
)
SELECT
  *
,NULL
,@TIMESTAMP
,@TIMESTAMP
from (
  SELECT
    path,
    crawled,
    stored
  FROM
    (
      VALUES
         @values
    ) as tmp (
  path,
  crawled,
  stored
          )
  EXCEPT
  (
  SELECT
    path,
    crawled,
    stored
  FROM
  crawler
  )
) as temp;
