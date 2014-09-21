

def follow_tags(db, department_id, tag_string):

  tags = tag_string.split(',')
  for tag in tags:
    tag = tag.strip()
    db.execute('''insert into tracked_hashtag (department_id, hashtag) values (?, ?)''',
      [department_id, tag])
  db.commit()

def get_timeline(db, department_id):

  query = '''
    select message.*, user.* from message, user, department, hashtag, tracked_hashtag where
    message.message_id = hashtag.message_id
    and hashtag.text = tracked_hashtag.hashtag 
    and message.author_id = user.user_id
    and department.department_id = ?
  '''

  cur = db.execute(query, [department_id])
  return cur.fetchall()

import sys
def get_muddas(db, department_id):
  query_assigned = '''
    select count(*) from message where
    message.status = 'Assigned' and
    message.assignee = %s
  '''%(department_id)

  query_solved = '''
    select count(*) from message where
    message.status = 'Fixed' and
    message.assignee = %s
  '''%(department_id)

  sys.stderr.write(repr(db.execute(query_assigned).fetchone()))
  return {
    'assigned': db.execute(query_assigned).fetchone()[0],
    'solved': db.execute(query_solved).fetchone()[0]
  }
