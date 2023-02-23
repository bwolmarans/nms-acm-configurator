# optional_params.py
def myfunc(a,b, *args):
    print(a); print(b)
    for ar in args:
      print(ar)
myfunc("a","b","c","d")
exit()

shopping_list = {}

def show_list(include_quantities=True):
    for item_name, quantity in shopping_list.items():
        if include_quantities:
            print(f"{quantity}x {item_name}")
        else:
            print(item_name)

def add_item(item_name, quantity=0):
    if item_name in shopping_list.keys():
        shopping_list[item_name] += quantity
    else:
        shopping_list[item_name] = quantity

add_item(item_name="Almond Milk")
add_item(item_name="Tofu", quantity=1)
add_item(item_name="Coffee", quantity=3)

show_list()

