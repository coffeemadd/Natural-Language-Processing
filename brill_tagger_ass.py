import nltk, re
from nltk.tag import brill, brill_trainer
from nltk.corpus import treebank
from nltk.tag import UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger
from nltk.corpus import wordnet as wn
import sys, http.client, urllib.request, urllib.parse, urllib.error, json
from os import listdir
from os.path import isfile,join

from pprint import pprint

import pickle

# make sure you've got some tdu -hs /home/projects/google-news-corpus/GoogleNews-vectors-negative300.binrain_sents!

def train_brill_tagger(initial_tagger, train_sents, **kwargs):
	templates = [
		brill.Template(brill.Pos([-1])),
		brill.Template(brill.Pos([1])),
		brill.Template(brill.Pos([-2])),
		brill.Template(brill.Pos([2])),
		brill.Template(brill.Pos([-2, -1])),
		brill.Template(brill.Pos([1, 2])),
		brill.Template(brill.Pos([-3, -2, -1])),
		brill.Template(brill.Pos([1, 2, 3])),
		brill.Template(brill.Pos([-1]), brill.Pos([1])),
		brill.Template(brill.Word([-1])),
		brill.Template(brill.Word([1])),
		brill.Template(brill.Word([-2])),
		brill.Template(brill.Word([2])),
		brill.Template(brill.Word([-2, -1])),
		brill.Template(brill.Word([1, 2])),
		brill.Template(brill.Word([-3, -2, -1])),
		brill.Template(brill.Word([1, 2, 3])),
		brill.Template(brill.Word([-1]), brill.Word([1])),
	]
	
	trainer = brill_trainer.BrillTaggerTrainer(initial_tagger, templates, deterministic=True)
	return trainer.train(train_sents, **kwargs)


def backoff_tagger(train_sents,tagger_classes,backoff=None):
	for cls in tagger_classes:
		backoff = cls(train_sents,backoff=backoff)
		return backoff



################## tagging ########################
def tag(wsji):
        train_sents = treebank.tagged_sents()
        wsji = wsji.rstrip()
        wsji = re.sub( r'\.$', '', wsji )
        wsji = re.sub( r'[,\?\!\.\{\}\(\)\'\"\`]', ' ', wsji )
        wsji = re.sub( r'\n', '', wsji )
        
        wsj = wsji.split(" ")
        

        #unigram_tagger = UnigramTagger(train_sents,cutoff=1,backoff=DefaultTagger('NNP'))
        #bigram_tagger  = BigramTagger(train_sents,cutoff=1,backoff=unigram_tagger)
        #trigram_tagger = TrigramTagger(train_sents,cutoff=4,backoff=bigram_tagger)
        #brill_tagger = train_brill_tagger(trigram_tagger,train_sents)
        #pickle.dump( brill_tagger, open( "my_tagger.pk", "wb" ) )

        brill_tagger = pickle.load(open("my_tagger.pk","rb"))

        tagged = brill_tagger.tag(wsj)

        possibles = []
        doubles = []
        for i in tagged:
                current = tagged.index(i)
                if (i[1] == "NNP" or i[1] == "NNPS"):
                        if(re.search('^[A-Z]',i[0])):
                                possibles.append(i[0])
                        try:
                                if (tagged[current+1][1] == 'NNP' or tagged[current+1][1] == 'NNPS'):
                                    if(re.search('^[A-Z]',tagged[current+1][0])):
                                        doubles.append(i[0] + " " + tagged[current+1][0])

                        except:
                                pass


        return (doubles,possibles)


###############checking with name lists #############################
def surnames(possibles):
        surnames = dict()
        defsurname = []
        with open("names.family.txt","r") as inF:
                for line in inF:
                        surnames[line.rstrip()] = True


        for fullname in possibles:
                if (fullname in surnames):
                        defsurname.append(fullname)

        return defsurname

                

def females(possibles):
        females = dict()
        deffemale = []
        with open("names.female.txt","r") as inF:
                for line in inF:
                        females[line.rstrip()] = True

        for women in possibles:
                if (women in females):
                        deffemale.append(women)

        return deffemale


def males(possibles):
        males = dict()
        defmale = []
        with open("names.male.txt","r") as inF:
                for line in inF:
                        males[line.rstrip()] = True

        for men in possibles:
                if (men in males):
                        defmale.append(men)
        return defmale


def titleCheck(titles,doubles,j):
        deftitle = []
        for i in doubles:
                parts = i.split(' ')
                title = parts[j]
                if title in titles:
                        deftitle.append(i)
        return deftitle


def both(doubles,surnames,females,males):
        defboth = []
        for i in doubles:
                parts = i.split(' ')
                if ((parts[0] in (females)) and (parts[1] in surnames)):
                        defboth.append(i)
                elif ((parts[0] in (males)) and (parts[1] in surnames)):
                        defboth.append(i)
                elif((parts[0] in (males)) and (len(parts[1]) == 1)):
                        defboth.append(i)
                elif((parts[0] in (females)) and (len(parts[1]) == 1)):
                        defboth.append(i)

        return defboth




################ Wiki NER ###########################

def get_url( domain, url ) :

  # Headers are used if you need authentication
  headers = {}


  try:
    conn = http.client.HTTPSConnection( domain )
    conn.request("GET", url, "", headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data 
  except Exception as e:
    # These are standard elements in every error.
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

  return None


# If this is included as a module, you have access to the above function
# without "running" the following piece of code.
# Usually, you place functions in a file and their tests in chunks like below.

def wiki(query):
        if __name__ == '__main__' : 

                # Call our function.
                url_data = get_url( 'en.wikipedia.org', '/w/api.php?action=query&list=search&format=json&srsearch=' + query )

                # We know how our function fails - graceful exit if we have failed.
                if url_data is None :
                        print( "Failed to get data ... Can not proceed." )
                        #Graceful exit.
                        sys.exit()

                

                url_text = None
                try:
                    # http.client socket returns bytes - we convert this to utf-8
                    url_data = url_data.decode( "utf-8" ) 
                    # Convert the structured json string into a python variable 
                    url_data = json.loads( url_data )
                    
                    # Now we extract just the titles
                    titles = [ i['title'] for i in url_data['query']['search'] ]

                    # Make sure we can plug these into urls:
                    url_titles = [ urllib.parse.quote_plus(i) for i in titles ]

                    url_text = get_url('en.wikipedia.org', '/w/api.php?format=json&action=query&prop=extracts&exlimit=max&explaintext&exintro&titles=' + url_titles[0])


                    url_text = url_text.decode( "utf-8" )
                except:
                    pass
                
                return url_text
                          
############### Wordnet Definition ###################

def wordnet(word):
        syns = wn.synsets(word)
        try:
                answer = syns[0].definition()
        except:
                answer = None

        return answer




## >>>>>>>>>> categorise <<<<<<<<<<<<
  
def categorise(url_text):
        
  p = 0
  o = 0
  l = 0
  b = 0

  if(url_text):
      # People:

      pSearch = ['died', 'lived', 'born', 'OM', 'MBE', 'OBE']
  
      for i in pSearch:
              if i in url_text:
                p = p + 1

            
      # Organisation

      oSearch = ['corporation', 'corporate', 'company', 'organisation', 'business']
      for i in oSearch:
            if i in url_text:
                o = o + 1


      # Location

      lSearch = ['country', 'city', 'state','north', 'south', 'east', 'west', 'located',]
      for i in lSearch:
            if i in url_text.lower():
                l = l + 1

      oSearch = ['object','thing','used']
      for i in oSearch:
            if i in url_text.lower():
                b = b + 1
            

  answer = ""
  maxi = max(l,o,p,b)
  if maxi == 0:
          answer = "none"
  elif maxi == l:
          answer = "location"
  elif maxi == p:
          answer = "person"
  elif maxi == o:
          answer = "organisation"
  else:
          answer = "none"

  return answer

################ main ############################
wsji = ""
wsjia = []
mypath = "wsj_New_test_data/wsj_New_test_data"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for i in onlyfiles:
        file = open((mypath+ "/" + i), "r")
        line = file.readline()
        wsji = wsji + line
        wsjia.append(line)
file.close()
(doubles,possibles) = tag(wsji)

names = ["the","people"]

for i in range(len(onlyfiles)):
        file = open(mypath+ "/done/" + onlyfiles[i], "w")
        for n in names:
            if n in wsji[i]:
                wsji[i] = re.sub(n,"<PERSON>" + n + "<\PERSON>",wsji[i])
        file.write(wsji[i])
        file.close()

surnames = surnames(possibles)
females = females(possibles)
males = males(possibles)
        
titles = ["Mr","Mrs","Miss","Ms","Prof","Professor","Dr","Doctor","Sir"]
bustitles = ["Co","Corp","Inc","International","Ltd","Industries"]
withTitle = titleCheck(titles,doubles,0)
withBus = titleCheck(bustitles,doubles,1)

old = []
new = []
growing = True

while growing:

        old = new
                
        for i in old:
                try:
                        parts = i.split(' ')
                        surnames = list(set(surnames + [parts[1]]))
                except:
                        pass

        boths = both(doubles,surnames,females,males)
        

        new = list(set(withTitle + boths))

        combined = list(set(surnames + females + males))

        splitUp = []
        for i in new:
                parts = i.split(' ')
                splitUp = splitUp + parts

        for i in combined:
                if i in splitUp:
                        new.append(i)
                else:
                        pass

        if (len(old) == len(new)):
                growing = False


forCheck = list((set(doubles)).difference(set(new))) + list(set(possibles))
for i in forCheck:
        if i in splitUp:
                forCheck = list(filter((i).__ne__, forCheck))

names = new
location = []
organisation = withBus

for i in forCheck:
            i = re.sub("\s+","",i) 
            if(len(i) == 1):
                try:
                    forCheck.remove(i)
                except:
                    pass

for i in forCheck:
        text = wordnet(i)
        if(not text):
                text = wiki(i)
        answer = categorise(text)
        if answer == "person":
                names.append(i)
                print("person: ",i)
        elif answer == "location":
                location.append(i)
                print("location: ",i)
        elif answer == "organisation":
                organisation.append(i)
                print("organisation: ",i)

file1 = open(mypath+ "/doneDemo/people.txt","w")
for i in range(len(names)):
        file1.write(names[i] + "\n")
file1.close()

file2 = open(mypath+ "/doneDemo/organisation.txt","w")
for i in range(len(organisation)):
        file2.write(organisation[i] + "\n")
file2.close()

file3 = open(mypath+ "/doneDemo/location.txt","w")
for i in range(len(location)):
        file3.write(location[i] + "\n")
file3.close()



for i in range(len(onlyfiles)):
        file = open(mypath+ "/doneDemo/" + onlyfiles[i], "w")
        for n in names:
            if n in wsjia[i]:
                wsjia[i] = re.sub(n,"<PERSON>" + n + "<\PERSON>",wsjia[i])
        for o in organisation:
            if o in wsjia[i]:
                wsjia[i] = re.sub(o,"<ORGANISATION>" + o + "<\ORGANISATION>",wsjia[i])
        for l in location:
            if l in wsjia[i]:
                wsjia[i] = re.sub(l,"<LOCATION>" + l + "<\LOCATION>",wsjia[i])
        file.write(wsjia[i])
        file.close()
        
