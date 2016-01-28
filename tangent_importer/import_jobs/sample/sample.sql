INSERT IGNORE INTO tbl_DB_AccountNew
    (Id, AccountNo, StatementedBranch, CustomerName, CreditLimit, Address1,
        Address2, Address3, Address4, Postcode, Phone, TermsText, OpenedDate,
        ModifiedDate, IsDeleted)
VALUES
    (NULL, %(ACCNO)s, %(STBR)s, %(CUSTOMER)s, %(LIMIT)s, %(ADDRESS01)s,
        %(ADDRESS02)s, %(ADDRESS03)s, %(ADDRESS04)s, %(ADDRESS05)s,
        %(TELEPHONE)s, %(TERMS)s, STR_TO_DATE(%(OPENED)s, "%%d/%%m/%%Y"),
        NOW(), 'N')
