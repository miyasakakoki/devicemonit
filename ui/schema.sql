PRAGMA foreign_keys = ON;

drop table if exists User;
create table User(
	uid integer primary key autoincrement, 
	email text not null,
	name text not null,
	pass text not null
);

insert into User( email, name, pass ) values( "asdf@asdf", "Test User", "password" );

drop table if exists devices;
create table devices(
	uid integer,
	did text not null,
	name text not null,
	description text not null,
	primary key( uid, did ),
	foreign key( uid ) references User(uid) on delete cascade on update cascade
);




