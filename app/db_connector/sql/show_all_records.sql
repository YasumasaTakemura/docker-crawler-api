SELECT
    path
FROM
    crawler
WHERE
    crawled = FALSE
ORDER BY
    created_at
