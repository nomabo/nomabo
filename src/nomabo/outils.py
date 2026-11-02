"""Fonctions utilitaires de nomabo."""

def smart_max(object, val_temp = [], ref_temp = []):
    '''
    Returns the maximum value and (and its reference) of any object as a tuple (maximum, reference).
    Only numbers are taken into account.

    - object : the object for which we wish to find the maximum
    - val_temp : path of the values
    - ref_temp : path of the references 

    The paths have the following form : [(type,key), ... , (type,key)]
    '''

    object_type = type(object)

    L_val = []
    L_ref = []

    if object_type == list:
        for i in range(len(object)):
            current_val = object[i]
            current_ref = object[i]
            for j in range(len(val_temp)):
                current_val = current_val[val_temp[j][1]]
            for k in range(len(ref_temp)):
                current_ref = current_ref[ref_temp[k][1]]

            L_val.append(current_val)
            if ref_temp == []:
                Lref.append(i)
            else:
                L_ref.append(current_ref)

    elif object_type == dict:
        for key in object:
            current_val = object[key]
            current_ref = object[key]
            for j in range(len(val_temp)):
                current_val = current_val[val_temp[j][1]]
            for k in range(len(ref_temp)):
                current_ref = current_ref[ref_temp[k][1]]

            L_val.append(current_val)
            if ref_temp == []:
                L_ref.append(key)
            else:
                L_ref.append(current_ref)

    maximum = None
    for i in range(len(L_val)):
        if type(L_val[i]) == int or type(L_val[i]) == float:
            if maximum == None:
                maximum = L_val[i]
            elif L_val[i] > maximum:
                maximum = L_val[i]
                index = i

    if maximum == None:
        return None
    else:
        return L_val[index], L_ref[index] 

def smart_min(object, val_temp = [], ref_temp = []):
    '''
    Returns the minimum value and (and its reference) of any object as a tuple (minimum, reference).
    Only numbers are taken into account.

    - object : the object for which we wish to find the minimum
    - val_temp : path of the values
    - ref_temp : path of the references 

    The paths have the following form : [(type,key), ... , (type,key)]
    '''

    object_type = type(object)

    L_val = []
    L_ref = []

    if object_type == list:
        for i in range(len(object)):
            current_val = object[i]
            current_ref = object[i]
            for j in range(len(val_temp)):
                current_val = current_val[val_temp[j][1]]
            for k in range(len(ref_temp)):
                current_ref = current_ref[ref_temp[k][1]]

            L_val.append(current_val)
            if ref_temp == []:
                L_ref.append(i)
            else:
                L_ref.append(current_ref)

    elif object_type == dict:
        for key in object:
            current_val = object[key]
            current_ref = object[key]
            for j in range(len(val_temp)):
                current_val = current_val[val_temp[j][1]]
            for k in range(len(ref_temp)):
                current_ref = current_ref[ref_temp[k][1]]

            L_val.append(current_val)
            if ref_temp == []:
                L_ref.append(key)
            else:
                L_ref.append(current_ref)

    minimum = None
    for i in range(len(L_val)):
        if type(L_val[i]) == int or type(L_val[i]) == float:
            if minimum == None:
                minimum = L_val[i]
            elif L_val[i] < minimum:
                minimum = L_val[i]
                index = i

    if minimum == None:
        return None
    else:
        return L_val[index], L_ref[index] 


