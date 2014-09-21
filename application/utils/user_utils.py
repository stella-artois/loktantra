# I define helper functions for users.

def get_mudda_count(db, user_id):
  """Returns count of muddas posted by this user.
  Args:
    db: Returns get_db object.
    user_id: User whose muddas needs to be queried.
  Returns:
    muddas: Count of muddas.
  """
  muddas = db.execute('''select count(*) from message where
      author_id = %s''' % (user_id))
  return muddas.fetchone()[0]

def get_user_reputation(db, user_id):
  """Returns reputation of the user.
  Args:
    db: Returns get_db object.
    user_id: User whose reputation needs to be queried.
  Returns:
    reputation: An integer representing user's reputation.
  """
  muddas = db.execute('''select count(*) from message where
      author_id = %s''' % (user_id))
  return muddas.fetchone()[0]

def force_follow_department(db):
  """Forces a user to follow some departments
  on some pre conceived notions. [citation required.]
  """

  db.execute('''insert or ignore into follower(who_id, whom_id) select user_id, department_id from
      user, department where user.city = department.city''')
  db.commit()
