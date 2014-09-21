create table if not exists user (
  user_id integer primary key autoincrement,
  full_name text not null,
  rep integer default 0 not null,
  username text not null,
  email text not null,
  birth_date date not null,
  aadhar_number integer not null,
  city text not null,
  state text not null,
  pw_hash text not null
);

create table if not exists department (
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

create table if not exists follower (
  who_id integer,
  whom_id integer
);

create table if not exists message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  pub_date integer
);

create table if not exists hashtag (
  message_id integer not null,
  text text not null
);
