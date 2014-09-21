drop table if exists user;
create table user (
  user_id integer primary key autoincrement,
  full_name text not null,
  username text not null,
  email text not null,
  birth_date date not null,
  city text not null,
  state text not null,
  pw_hash text not null
);

drop table if exists department;
create table department (
  department_id integer primary key autoincrement,
  department_name text not null,
  num_issues_assigned integer default 0 not null,
  num_issues_solved integer default 0 not null,
  verified integer default 0 not null,
  username text not null,
  email text not null,
  city text not null,
  state text not null,
  pw_hash text not null
);

drop table if exists follower;
create table follower (
  who_id integer,
  whom_id integer
);

drop table if exists message;
create table message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  plus_one_count integer default 0 not null,
  location text not null,
  status text default 'new' not null,
  assignee text,
  pub_date integer
);

drop table if exists hashtag;
create table hashtag (
  message_id integer not null,
  text text not null
);

drop table if exists tracked_hashtag;
create table tracked_hashtag (
  department_id integer not null,
  hashtag text not null
);

drop table if exists plus_one;
create table plus_one (
  message_id integer not null,
  user_id integer not null
);

drop table if exists comment;
create table comment (
  text text not null,
  user_id integer not null,
  message_id integer not null
);
