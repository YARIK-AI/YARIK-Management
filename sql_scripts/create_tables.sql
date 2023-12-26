create schema etl;

create table if not exists etl.components 
(
	id smallint,
	"name" varchar(63),
	description text,
	primary key (id)
);


create table if not exists etl.files
(
	id smallint,
	"name" varchar(63),
	description text,
	filename varchar(255),
	ftype varchar(5),
	fencoding varchar(15),
	gitslug varchar(1024),
	xslt_gitslug varchar(1024),
	xsd_gitslug varchar(1024),
	component_id smallint REFERENCES etl.components (id),
	primary key (id)
);

create table if not exists etl.parameters
(
	id smallint,
	"name" varchar(63),
	description text,
	absxpath text,
	value text,
	file_id smallint REFERENCES etl.files (id),
	primary key (id)
);

