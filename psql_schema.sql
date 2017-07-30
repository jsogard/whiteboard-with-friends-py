create table Username(
	id serial primary key unique,
	username varchar(64) unique not null,
	password char(64) not null
);

create table Board(
	id serial primary key unique,
	user_id int references username(id),
	name varchar(64) not null,
	last_modified timestamp not null,
	public boolean not null default false
);

create table Permission(
	board_id int references board(id),
	user_id int references username(id),
	write boolean not null
);
