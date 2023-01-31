# Fix Python 2.x.
try: input = raw_input
except NameError: pass
#print("Hi " + input("Say something: "))
nms_instances = {'nms_instances': [{'hostname': 'brett1.seattleis.cool', 'username': 'admin', 'password': 'Testenv12#'}, {'hostname': 'brett5.seattleis.cool', 'username': 'admin', 'password': 'Testenv12#'}]}
#print(nms_instances)
x = {'stuff': [{'a': '1', 'b': '2', 'c': '3'}, {'e': '4', 'f': '5', 'g': '6'}]}
print(x)
x['stuff'].append({'h': '7', 'i': '8', 'j': '9'}) 
print(x)
