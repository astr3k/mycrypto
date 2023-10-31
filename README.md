# mycrypto

A terminal program to keep track of your crypto in one shot. Helps to check of the percentage invested and the return.
It works with [SQLite](https://sqlite.org).
The user should be able to insert, edit and delete data on a table that is created if not exists when running the program:

```
sqlite> .schema
CREATE TABLE crypto (
            'date' datetime not null primary key default current_timestamp,
            'cents' integeer not null,
            'amount' real not null,
            'code' char(3) not null,
            'coin' varchar(15) not null,
            'remarks' varchar(150) not null
        );
```
Depends on [requests](https://pypi.org/project/requests/) and [tabulate](https://pypi.org/project/tabulate/) to create a very simple table:

invest |  % | amount | code | avg price € | price € | total € | profit € | profit % | price USB | price ₿ | total ₿ | price $/₿ | price €/₿
------ | -- | ------ | ---- | ----------- | ------- | ------- | -------- | -------- | --------  | ------- | ------- | --------- | ---------


