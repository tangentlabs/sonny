INSERT IGNORE INTO tbl_DB_AccountNew
    (Id, AccountNo, CustomerName, Address1,
        Address2, Address3, Address4, Postcode, Phone, OpenedDate,
        ModifiedDate, IsDeleted)
VALUES
    (NULL, %(Account Number)s, %(Customer Name)s, %(Address 1)s,
        %(Address 2)s, %(Address 3)s, %(Address 4)s,
        %(Telephone)s, STR_TO_DATE(%(Opened)s, "%%d/%%m/%%Y"),
        NOW(), 'N')
