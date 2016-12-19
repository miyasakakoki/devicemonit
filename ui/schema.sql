PRAGMA foreign_keys = ON;

drop table if exists User;
create table User(
	uid integer primary key autoincrement, 
	name text not null,
	pass text not null
);

drop table if exists devices;
create table devices(
	uid integer,
	did text not null,
	name text not null,
	description text not null,
	seq integer ,
	primary key( uid, did ),
	foreing key( uid ) references User(uid) on delete cascade on update cascade
);




