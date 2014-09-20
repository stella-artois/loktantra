# I define helper functions for messages.

def extract_hashtags(text):
  """Responsible for extracting hashtags from tweet text.

  Args:
    text: Tweet text.
  Returns:
    hashtags: A list of hashtags.
  """
  return [_[1:] for _ in text.split() if _.startswith('#')]
