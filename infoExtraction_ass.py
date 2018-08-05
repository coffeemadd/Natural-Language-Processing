import nltk, re
from nltk.tag import brill, brill_trainer
from nltk.corpus import treebank
from nltk.tag import UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger
from nltk.corpus import wordnet as wn
import sys, http.client, urllib.request, urllib.parse, urllib.error, json
from os import listdir
from os.path import isfile,join
from shutil import copytree

from pprint import pprint

import pickle

def speaker(email, surnames, male, female,pasts):
        
        speaker = ""
        reg = ["speaker:","who:","WHO:","SPEAKER:","Speaker:","Who:"]

        found = False
        abstract = False
        
        for i in range(len(email)):
                if((("Abstract" in email[i]) or abstract) and ("host" not in email[i].lower())):
                        abstract = True
                else:
                        abstract = False

                
                for j in reg:
                        if (j in email[i]):
                                speaker = email[i]
                                speaker = speaker.replace(j,"")
                                speaker = speaker.replace(":","")
                                speaker = speaker.replace('\n',"")
                                speaker = re.sub(',.+',"",speaker)
                                while(speaker[0] == " "):
                                        speaker = speaker.replace(" ","",1)
                                found = True
                                break
                if(found):
                        break
                if(abstract):
                        surnames = set(surnames)
                        male = set(male)
                        female = set(female)
                        
                        if (set(email[i].split()) & surnames):
                                speaker = email[i]
                                speaker = speaker.rstrip()
                                speaker = re.sub('^(\t*\s*)',"",speaker)
                                speaker = re.sub('[,-].+',"",speaker)
                                
                        if ((set(email[i].split()) & male) and (found == False)):
                                found = True
                                speaker = email[i]
                                speaker = speaker.rstrip()
                                speaker = re.sub('^(\t*\s*)',"",speaker)
                                speaker = re.sub('[,-].+',"",speaker)

                        if ((set(email[i].split()) & female) and (found == False)):
                                found = True
                                speaker = email[i]
                                speaker = speaker.rstrip()
                                speaker = re.sub('^(\t*\s*)',"",speaker)
                                speaker = re.sub('[,-].+',"",speaker)


        if(not speaker):
                for i in range(len(email)):
                        for j in pasts:
                                k = j.split()
                                for p in k:
                                        if p in email[i]:
                                                speaker = email[i].rstrip()
                                                speaker = re.sub('^(\t*\s*)',"",speaker)

        if(speaker):
                pasts.append(speaker)
                for i in range(len(email)):
                        email[i] = re.sub(speaker, "<speaker>" + speaker + "</speaker>", email[i])
        

        return (email,pasts)


def location(email,pastl):

        location = ""
        reg = ["PLACE","WHERE","place","where","Place","Where"]
        reg2 = ["hall","theatre","room"]
        found = False
        abstract = False
        for i in range(len(email)):
                for j in reg:
                        if (j in email[i]):
                                location = email[i]
                                location = location.replace(j,"")
                                location = location.replace(":","")
                                location = location.rstrip()
                                location = re.sub('^(\t*\s*)',"",location)
                                found = True
                                break
                if(found):
                        break

                for j in reg2:
                        if( abstract and (len(email[i]) < 50)):
                                if (j in email[i].lower()):
                                        location = email[i]
                                        location = location.rstrip()
                                        location = re.sub('^(\t*\s*)',"",location)
                                        found = True
                                        break
                if(found):
                        break

        if(not location):
                for i in range(len(email)):
                        for j in pastl:
                                k = j.split()
                                for p in k:
                                        if p in email[i]:
                                                location = email[i].rstrip()
                                                location = re.sub('^(\t*\s*)',"",location)

                                                
        
        if(location):
                pastl.append(location)
                for i in range(len(email)):
                        try:
                                email[i] = re.sub(location,"<location>" + location + "</location>", email[i])
                        except:
                                pass

        return (email,pastl)



def time(email):

        stime = ""
        etime = ""
        nosign = False
        done = False
        
        for i in range(len(email)):
                answer = re.search(('Time:\s*\d+:\d+\s*(AM|PM)' ),email[i])
                if(not answer):
                        nosign = True
                        answer = re.search(('Time:\s*\d+:\d+\s*' ),email[i])
                        answer2 = re.search(('Time:\s*\d+:\d+\s*-\s*\d+:\d+\s*' ),email[i])
                else:
                        nosign = False
                        answer2 = re.search(('Time:\s*\d+:\d+\s*(AM|PM)-\s*\d+:\d+\s*(AM|PM)' ),email[i])

                if (answer2):
                        answer2 = answer2.group()
                        if(nosign):
                                stime = re.search(('\d+:\d+'),email[i])
                                stime = stime.group()

                                etime = re.search(('-\s*\d+:\d+'),email[i])
                                etime = etime.group()
                                etime = re.search(('\d+:\d+'),etime)
                                etime = etime.group()
                                

                        
                elif (answer):
                        stime = re.search(('\d+:\d+'),email[i])
                        stime = stime.group()



        if(stime):
                for i in range(len(email)):

                        if(re.search(stime,email[i])):
                                email[i] = re.sub(stime, "<stime>" + stime + "</stime>", email[i])
                                if(etime):
                                        email[i] = re.sub(etime, "<etime>" + etime + "</etime>", email[i])

                


        return email




def sentences(email):

        inpara = False
        abstract = False
        for i in range(len(email)):
                search = re.match("Abstract:", email[i-1])
                if (search != None or abstract):
                        abstract = True
                        search = re.match("<paragraph>", email[i])
                        if((search != None) or inpara):
                                inpara = True
                                email[i] = re.sub("<paragraph>", "<paragraph><sentence>",email[i])

                                email[i] = re.sub(("</paragraph>"), ("</sentence></paragraph>"), email[i])
                                answer = re.findall(('[\.\?!\)]\s+([A-Z0-9]|\n)'), email[i])
                                answer = list(set(answer))
                                if (answer):
                                        for j in answer:
                                                j = str(j)
                                                j = j[-1]
                                                email[i] = re.sub(('\.\s+' + j), (".</sentence><sentence>" + j),email[i])
                        else:
                                s1 = re.search("^[A-Z]", email[i])
                                s2 = re.search(('[\.\?!\):]\n$'), email[i])

                                if(s1 and s2):
                                        email[i] = "<sentence>" + (email[i].rstrip()) + "<\sentence>\n"
                
    

        return email



def paragraphs(email):
        abstract = False
        inpara = False
        
        for i in range(len(email)):
                search = re.match("Abstract:", email[i-1])
                if (search != None or abstract):
                        abstract = True
                        para = re.search(r'[\.\?\)!]$' ,email[i])
                        para2 = re.search('^\s*\t*[A-Z]',email[i])
                        
                        if(para2 and (not inpara) and (len(email[i])>60) and (":" not in email[i])):
                                email[i] = "<paragraph>" + email[i]
                                inpara = True

                        if (para and (inpara)):
                                email[i] = email[i].rstrip() + "</paragraph> \n"
                                inpara = False
                        

        return email






################ main ############################

mypath = "seminar_testdata/test_untagged"
surnames = dict()
male = dict()
female = dict()
pastl = []
pasts = []

with open("names.family.txt","r") as inF:
                for line in inF:
                        surnames[line.rstrip()] = True


with open("names.female.txt","r") as inF:
                for line in inF:
                        female[line.rstrip()] = True


with open("names.male.txt","r") as inF:
                for line in inF:
                        male[line.rstrip()] = True

        
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
del onlyfiles[0]

for i in onlyfiles:
        email = []
        file = open((mypath+ "/" + i), "r")
        for line in file:
                email.append(line)

        (email,pasts) = speaker(email,surnames,male,female,pasts)
        email = time(email)
        (email,pastl) = location(email,pastl)
        email = paragraphs(email)
        email = sentences(email)

        file2 = open("info_extraction/done/" + i, "w")
        for j in email:
                file2.write(j)

        file2.close()
        file.close()




       
  



