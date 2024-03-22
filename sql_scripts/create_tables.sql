create schema artifacts;

create table if not exists artifacts.modules
(
	id smallint,
	"name" varchar(31),
	description text,
	primary key (id)
);

create table if not exists artifacts.components 
(
	id smallint,
	"name" varchar(63),
	description text,
	module_id smallint REFERENCES artifacts.modules (id),
	primary key (id)
);

create table if not exists artifacts.applications
(
	id smallint,
	"name" varchar(63),
	description text,
	component_id smallint REFERENCES artifacts.components (id),
	primary key (id)
);

create table if not exists artifacts.instances
(
	id smallint,
	"name" varchar(63),
	"version" varchar(31),
	description text,
	app_id smallint REFERENCES artifacts.applications (id),
	primary key (id)
);

create table if not exists artifacts.files
(
	id smallint,
	"name" varchar(63),
	description text,
	filename varchar(255),
	ftype varchar(5),
	fencoding varchar(15),
	path_prefix varchar(1024),
	gitslug_postfix varchar(1024),
	xslt_gitslug_postfix varchar(1024),
	xsd_gitslug_postfix varchar(1024),
	is_sync boolean not null,
	instance_id smallint REFERENCES artifacts.instances (id),
	primary key (id)
);

create table if not exists artifacts.parameters
(
	id smallint,
	"name" varchar(63),
	description text,
	absxpath text,
	value text,
	prev_value text,
	default_value text,
	input_type varchar(14),
	file_id smallint REFERENCES artifacts.files (id),
	primary key (id)
);