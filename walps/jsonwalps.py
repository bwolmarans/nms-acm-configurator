import re
data = """
     {
  key: "value",
  "key2": False,
  blah: True
}
"""
print(data)
data = re.sub("((?=\D)\w+):", r'"\1":',  data)
data = re.sub(": ((?=\D)\w+)", r':"\1"',  data)
print(data)
