def isPronounResolved(root):
    
    np = root[0][0]
    
    print np
    
    flag = False
    
    for token in np:
        if token.label().startswith('NN'):
            flag = True
            break
    
    return flag
