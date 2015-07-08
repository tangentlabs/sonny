INSERT IGNORE INTO tbl_DB_AccountNew
(Id, AccountNo, CustomerName, Address1,
    Address2, Address3, Address4, Postcode, Phone, OpenedDate,
    ModifiedDate, IsDeleted)
VALUES
(NULL, %s, %s, %s, %s, %s, %s, %s, %s,
    STR_TO_DATE(%s, "%%d/%%m/%%Y"), NOW(), 'N')
