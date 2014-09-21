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

def extract_hashtags(text):
  """Responsible for extracting hashtags from tweet text.

  Args:
    text: Tweet text.
  Returns:
    hashtags: A list of hashtags.
  """
  return [_[1:] for _ in text.split() if _.startswith('#')]
