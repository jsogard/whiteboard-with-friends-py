drop table if exists User;
drop table if exists Board;

create table User(
	id integer primary key autoincrement,
	username text not null,
	password char(64) not null
);

create table Board(
	id integer primary key autoincrement,
	userId integer not null,
	name char(64) not null,
	lastModified datetime NOT NULL,
	foreign key(userId) references User(id)
);

