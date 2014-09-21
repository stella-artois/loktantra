create table if not exists user (
  user_id integer primary key autoincrement,
  full_name text not null,
  username text not null,
  email text not null,
  birth_date date not null,
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
  email text not null default "piyush.devel@gmail.com",
  city text not null,
  state text not null,
  pw_hash text not null
);
/*insert into department values(50000, 'd',1, 2, 2, 'd', 'cow@bullocks.cow', 'd', 'd', 'd');
delete from department;*/

create table if not exists follower (
  who_id integer,
  whom_id integer,
  primary key(who_id, whom_id)
);

create table if not exists message (
  message_id integer primary key autoincrement,
  author_id integer not null,
  text text not null,
  plus_one_count integer default 0 not null,
  location text not null,
  status text default 'new' not null,
  assignee text,
  tokens text not  null,
  pub_date integer
);

create table if not exists hashtag (
  message_id integer not null,
  text text not null
);

create table if not exists tracked_hashtag (
  department_id integer not null,
  hashtag text not null
);

create table if not exists plus_one (
  message_id integer not null,
  user_id integer not null
);

create table if not exists comment (
  text text not null,
  user_id integer not null,
  message_id integer not null
);
