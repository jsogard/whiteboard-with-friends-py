drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

drop table if exists user;
create table User (
	id integer primary key autoincrement,
	username text not null,
	password char(64)
);