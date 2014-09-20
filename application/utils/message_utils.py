# I define helper functions for messages.

import sys
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
    sys.stderr.write("Here\n\nWTF!!\n")
    db.execute('''insert into plus_one (user_id, message_id) values (?, ?)''',
        [user_id, message_id])
    db.commit()
    db.execute('''update message set plus_one_count=plus_one_count+1
        where message_id=%d''' % (message_id))
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
  db.execute('''insert into table comment (user_id, message_id, text)
      values (?, ?, ?)''', [user_id, message_id, text])
  db.commit()
  return text
