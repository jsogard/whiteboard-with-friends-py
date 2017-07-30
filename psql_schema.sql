create table Username(
	id serial primary key,
	username varchar(64) not null,
	password char(64) not null
);