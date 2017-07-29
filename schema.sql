drop table if exists User;
drop table if exists Board;
drop table if exists Permission;

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
	isPublic boolean not null,
	foreign key(userId) references User(id)
);

create table Permission(
	boardId integer not null,
	userId integer not null,
	write boolean not null,
	foreign key(boardId) references Board(id),
	foreign key(userId) references User(id)
);