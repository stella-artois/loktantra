# I define helper functions for search.


def get_messages_by_hashtag(db, hashtag):
  """Returns list of messages containing given hashtag.
  Args:
    db: Returns get_db object.
    hashtag: Hashtag which needs to be searched.
  Returns:
    messages: List of messages ids.
  """

  #TODO(Piyush): Fetch only few messages at a time.
  messages = db.execute('''select message_id from hashtag where
      hashtag = %s''' % (hashtag))
  return messages.fetchall()
