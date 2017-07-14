drop table if not exists User;

create table User(
	id integer primary key autoincrement,
	username text not null,
	password char(64) not null
);