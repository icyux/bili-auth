import json


def formatJson(s):
	outOfValue = True
	isComment = False
	result = ''
	for i, c in enumerate(s):

		# remove line comment
		if isComment:
			if c == '\n':
				isComment = False

		# remove tail comma
		elif outOfValue and c == ',':
			j = i + 1
			while j < len(s) and s[j] in (' ', '\t', '\n'):
				j += 1

			if s[j] not in (']', '}'):
				result += ','

		elif c == '"':
			outOfValue = not outOfValue
			result += '"'

		elif outOfValue and c == '/' and s[i+1] == '/':
			isComment = True

		else:
			result += c

	return result


def readConfig(path):
	with open(path) as f:
		data = f.read()

	formatted = formatJson(data)
	return json.loads(formatted)
