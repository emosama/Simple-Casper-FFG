'''
已完成
'''
import copy
import json

def serialization(data):
    copy_data = copy.deepcopy(data)
    if hasattr(copy_data, "__dict__"):
        copy_data = copy_data.__dict__
        for each in copy_data.keys():
            copy_data[each] = serialization(copy_data[each])
        return copy_data

    elif type(copy_data).__name__ == "dict":
        for each in copy_data.keys():
            copy_data[each] = serialization(copy_data[each])
        return copy_data

    elif type(copy_data).__name__ == "list":
        for i in range(len(copy_data)):
            copy_data[i] = serialization(copy_data[i])
        return copy_data
    elif type(copy_data).__name__ == "set":
        list_set = []
        for each in copy_data:
            list_set.append(serialization(each))
        return list_set
    else:
        return copy_data

def toString(obj):
    return json.dumps(serialization(obj))