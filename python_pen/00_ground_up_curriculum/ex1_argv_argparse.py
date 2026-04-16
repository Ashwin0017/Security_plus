import sys
print(f"Number of arguments : {len(sys.argv)}")
print(f"script name : {sys.argv[0]}")

for i, arg in enumerate(sys.argv[1:], start=1):
	print(f"argument {i} : {arg} (type : {type(arg).__name__})")

'''

What to notice:

Every value is str regardless of what you typed — 123 comes in as "123", not int
Quoting "hello world" makes it one argument, not two
No arguments → len(sys.argv) is 1, not 0 (script name is always there)


'''
