# mycrypto

A terminal program to keep track of your crypto in one shot. Helps to check of the percentage invested and the return.
It works with [SQLite](https://sqlite.org).
The user should be able to insert, delete and modify data on a very simple table that is created if not exists when running the program:

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
The output is a very simple table:

invest |  % | amount | code | avg price € | price € | total € | profit € | profit % | price ₿ | total ₿
------ | -- | ------ | ---- | ----------- | ------- | ------- | -------- | -------- | ------- | -------   


