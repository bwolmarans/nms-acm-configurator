import yaml

if __name__ == '__main__':

    stream = open("nms_instances.yaml", 'r')
    dic = yaml.load(stream, Loader=yaml.FullLoader)
    print(" ")
    print(dic)
    print("------------------------------------------------------")
    for key, value in dic.items():
        print (key + " : " + str(value))
    print("------------------------------------------------------")
    for item in dic['nms_instances']:
        print(item['hostname'] + " " + item['username'] + " " + item['password'])
