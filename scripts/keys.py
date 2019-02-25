def _read_first_line(name):
	f = open(name, 'r')
	return f.read().strip().split()[0]

def client_id():
	filename = "keys/CLIENT_ID"
	return _read_first_line(filename)

def client_secret():
	filename = "keys/CLIENT_SECRET"
	return _read_first_line(filename)