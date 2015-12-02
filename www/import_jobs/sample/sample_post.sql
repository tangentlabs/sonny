DELETE
    FROM tbl_DB_AccountNew
WHERE
    CustomerName NOT IN (
        SELECT
            C_CustomerName
        FROM
            tbl_DB_Customer
    )
