# Fix Python 2.x.
try: input = raw_input
except NameError: pass
print("Hi " + input("Say something: "))
