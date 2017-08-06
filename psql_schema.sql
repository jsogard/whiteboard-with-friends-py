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
	public privilege not null default 'RESTRICT' check (public != 'DELETE')
);

create type privilege AS ENUM ('DELETE', 'WRITE', 'READ', 'RESTRICT');

create table Permission(
	board_id int NOT NULL references board(id),
	user_id int NOT NULL references username(id),
	privilege privilege NOT NULL DEFAULT 'READ',
	PRIMARY KEY(board_id, user_id, privilege)
);
