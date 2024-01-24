# portfolio

A terminal program to keep track of your actives.
It works with [SQLite](https://sqlite.org) and [requests](https://pypi.org/project/requests/).
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
It needs a [TOR](https://www.torproject.org) service running to get the prices.
