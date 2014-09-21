# I define helper functions for messages.

TAGS = {
	'NORMAL_TEXT': 1,
	'HASH_TAG': 2,
	'PAGE': 3
}

def getTags(text):
  """Responsible for extracting hashtags from tweet text.

  Args:
    text: Tweet text.
  Returns:
    Tags: A list of tags with their corresponding type.
  """
  message = []
  words = text.split()
  for word in words:
  	if word[0] == '#':
  		message.append((word[1:], TAGS['HASH_TAG']))
  	elif word[0] == '@':
  		message.append((word[1:], TAGS['PAGE']))
  	else:
  		message.append((word, TAGS['NORMAL_TEXT']))
  return message

def get_message_as_token(text):
  return ',' + ','.join([token[0] for token in getTags(text)])

def extract_hashtags(text):
  """Responsible for extracting hashtags from tweet text.

  Args:
    text: Tweet text.
  Returns:
    hashtags: A list of hashtags.
  """
  return [_[1:] for _ in text.split() if _.startswith('#')]

def get_plus_ones(db, message_id):
  """Responsible for fetching user-ids, who upvoted
  a particular message.

  Args:
    message_id: message.message_id.
    db: get_db() object.
  Returns:
    list of memberids.
  """
  user_ids = db.execute('''select user_id from plus_one
  where %s = plus_one.message_id''' % message_id)
  return user_ids.fetchall()

def plus_one_message(db, message_id, user_id):
  """Responsible for plus oning a particular message.

  Args:
    message_id: message.message_id.
    db: get_db() object.
  Returns:
    None.
  """
  plus_ones = db.execute('''select * from plus_one
      where message_id=%d and user_id=%d'''
      % (int(message_id), int(user_id)))
  if not plus_ones.fetchone():
    db.execute('''insert into plus_one (user_id, message_id) values (?, ?)''',
        [user_id, message_id])
    db.commit()
    db.execute('''update message set plus_one_count=plus_one_count+1
        where message_id=%d''' % int(message_id))
    db.commit()

def minus_one_message(db, message_id, user_id):
  """Responsible for minus oning a particular message.

  Args:
    message_id: message.message_id.
    db: get_db() object.
  Returns:
    None.
  """
  plus_ones = db.execute('''select * from plus_one
      where message_id=%d and user_id=%d'''
      % (int(message_id), int(user_id)))
  if plus_ones.fetchone():
    db.execute('''delete from plus_one where user_id = %d
        and message_id = %d''' % (int(user_id) ,int(message_id)))
    db.commit()
    db.execute('''update message set plus_one_count=plus_one_count-1
        where message_id=%d''' % int(message_id))
    db.commit()

def make_comment(db, message_id, user_id, text):
  """Responsible for commenting on a particular post.

  Args:
    db: get_db() object.
    message_id: message.message_id.
    text: The content of the message.

  Returns:
    text: The content of the message. This is to ensure that
      only db committed messages are rendered.
  """
  db.execute('''insert into comment (user_id, message_id, text)
      values (?, ?, ?)''', [user_id, message_id, text])
  db.commit()
  return text

def get_comments(db, message_id, user_id):
  """Returns the list of comments on a particular mudda by an user.

  Args:
    db: get_db() object.
    message_id: message.message_id.

  Returns:
    List of comments posted in this message id.
  """
  message_rows = db.execute('''select * from comment
      where message_id=%s and
      user_id=%s''' % (message_id, user_id))
  messages = []
  row = message_rows.fetchone()
  while row:
    messages.append(row['text'])
    row = message_rows.fetchone()
  return messages

def is_upvoted(db, message_id, user_id):
  """Checks if a given message_id has been upvoted
  by a given user_id.

  Args:
    message_id: message.message_id.
    db: get_db() object.
    user_id: user.user_id.

  Returns:
    bool.
  """
  rows = db.execute('''select * from plus_one where user_id = %s and
  message_id = %s''' %(user_id, message_id))
  return True if rows.fetchone() else False
