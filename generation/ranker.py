import nltk
import requests
from bs4 import BeautifulSoup
from _collections import defaultdict

def get_score(question,q_type):
    
    payload = {'key': 'deepakkey', 'data': question}
    
    get_response = requests.get(url='http://service.afterthedeadline.com/stats',params=payload)
    
    #print get_response.text
    
    soup = BeautifulSoup(get_response.text,'html.parser')
    
    #print soup.prettify()
    
    L = soup.findAll('type')
    
    hasError = False
    no_of_errors = 0
    
    for l in L:
        if l.text == 'grammar':
            hasError = True
            break
    
    if hasError:
        P = l.parent()
    
        for p in P:
            if p.name == 'value':
                break
    
        no_of_errors = float(p.text)
    

    #print no_of_errors
    
    length = len(nltk.word_tokenize(question))
    
    #print length
    final_score = 1*length + 10 - (5*no_of_errors)
    
    if q_type == 'yes':
        final_score+=10
    elif q_type =='no':
        final_score-=5
    
    return final_score
    
def compare(t):
    
    return t[1]

def rank(question_type_list,N):
    
    type_to_questions = defaultdict(list)
    
    for pair in question_type_list:
        
        question = pair[0]
        question_type = pair[1]
        
        score = get_score(question,question_type)
        
        type_to_questions[question_type].append(tuple([question,score]))
    
    q_types = type_to_questions.keys()
    
    for q_type in q_types:
        
        q_list = type_to_questions[q_type]
        
        type_to_questions[q_type] = sorted(q_list,reverse=True,key=compare)
        
        
    #create a new merged list mixing questions of different types
    ranked_list = []
    
    yesQ = type_to_questions['yes']
    t1 = len(yesQ)
    
    whatQ = type_to_questions['what']
    t2 = len(whatQ)
    
    whoQ = type_to_questions['who']
    t3 = len(whoQ)
    
    noQ = type_to_questions['no']
    t4 = len(noQ)
    
    
    a1 = int(N*.5)
    if t1<a1:
        a1 = t1
    t1-=a1
        
    a2 = int(N*.2)
    if t2<a2:
        a2 = t2
    t2-=a2
    
    a3 = int(N*.2)
    if t3<a3:
        a3 = t3
    t3-=a3
        
    a4 = N-a1-a2-a3
    if t4<a4:
        a4 = t4
    t4-=a4
        
    total = a1+a2+a3+a4
    
    print total
    
    for i in range(a1):
        if i<len(yesQ):
            ranked_list.append(yesQ[i][0])    
    for i in range(a2):
        ranked_list.append(whatQ[i][0])
    for i in range(a3):
        ranked_list.append(whoQ[i][0])
    for i in range(a4):
        ranked_list.append(noQ[i][0])
        
    while(total<N):
        if t1>0:
            ranked_list.append(yesQ[a1][0])
            a1+=1
            t1-=1
        total+=1
    
    return ranked_list
        
questionList = [('Does most people learn English for practical rather than ideological reasons?','yes'),
                ('Did decolonisation proceed throughout the British Empire in the 1950s and 1960s?','yes'),
                ('Does english continue to be an official language of India?','yes'),
                ('Is also?','yes'),
                ('Is newspaper publishing book publishing?','yes'),
                ('Is english an official language in most countries?','no')]

print rank(questionList,3)
#question = 'Does most people learn English for practical rather than ideological reasons?'
#print get_score(question) 
