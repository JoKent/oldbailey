import urllib.request as ur
import urllib.error
from urllib.parse import quote
import csv
import os
import xml.etree.ElementTree as ET
import json
import hashlib

oburl = "https://www.oldbaileyonline.org/obapi/"
trialq = "text?div="
locq = "ob?term0=trialtext_"
term1 = "&term1=fromdate_"
term2 = "&term2=todate_"
	
def simplequery(url): #runs a simple query against an api 
	cachefile = getcachefilename(url)
	try:
		if os.path.isfile(cachefile):
			f = open(cachefile, 'r')
			return json.load(f)
		else:
			r = ur.Request(url)
			conn = ur.urlopen(r)
			if conn.status!=200:
				raise "Something went wrong"
			data = conn.read()
			str_data = data.decode('utf8')		
			js_data = json.loads(str_data)
			f = open(cachefile, 'w')
			json.dump(js_data, f)
			return js_data
	except Exception as e:
		raise e 

def xmlquery(url):
    try:
        r = ur.Request(url)
        conn = ur.urlopen(r)
        if conn.status!=200:
            raise "Something went wrong"
        data = conn.read()
        str_data = data.decode('utf8')	
        return str_data
    except Exception as e:
        raise e                  
            
def getcachefilename(url):
		object = hashlib.sha256()
		b = bytes(url, 'utf-8')
		object.update(b)
		cachefilename = "C:\\Users\\joken\\Documents\\scripts\\cache\\"+object.hexdigest()
		return cachefilename

############# # Parse XML with ElementTree
	

####### OB API queries 

def getbaileytrials(list,where):
    s=list[0]
    e=list[1]
    url = oburl+locq+where+term1+s+term2+e
    data = simplequery(url)
    trials = data["hits"]
    return trials
    
def gettrialdetails(trial):
    y = trial[:5]
    year = y.removeprefix('t')
    # print(year)
    trialinfo = list()
    offencelist = list()
    verdictlist = list()
    url = oburl+trialq+trial
    data = xmlquery(url)
    root = ET.fromstring(data) # Parse XML with ElementTree
    # print("tag=%s, attrib=%s" % (root.tag, root.attrib))
    place = None
    for location in root.iter('placeName'):
        for x in location.itertext():
            print("XXX value is <"+x+">")
            if "/n" not in x:
                place = x
        if place != None:
            print("Place updated to : "+place)
    for offence in root.iter('rs'): # get offences and verdicts
        for child in offence:
            # print(child.tag, child.attrib)
            if child.get('type') == "offenceCategory":
                offenceCategory = child.get('value')
                offenceid = child.get('inst')
                offence = {"offenceid":offenceid,"offenceCategory":offenceCategory}
                offencelist.append(offence)
            elif child.get('type') == "offenceSubcategory":
                offenceSubcategory = child.get('value')
                offenceid = child.get('inst')
                for o in offencelist:
                    if o.get('offenceid') == offenceid:
                       o["offenceSubcategory"] = offenceSubcategory   
            elif child.get('type') == "verdictCategory":
                verdictCategory = child.get('value')
                vid = child.get('inst')
                verdict = {"verdictid":vid,"verdict":verdictCategory}
                verdictlist.append(verdict)
    for person in root.iter('persName'): # get person details 
        if person.get('type') == "defendantName":
            age = None
            given = None
            surname = None
            id = person.get('id')
            # print("Defendant: "+id)
            for child in person:
                if child.get('type') == "surname":
                    surname = child.get('value')
                if child.get('type') == "given":
                    given = child.get('value')
                if child.get('type') == "gender":
                    gender = child.get('value')
                if child.get('type') == "age":
                    age = child.get('value')
            personinfo = {"trial":trial,"place":place,"year":year,"id":id,"given":given,"surname":surname,"gender":gender,"age":age}
            trialinfo.append(personinfo)
    for join in root.iter('join'): # get join details for person offence and verdict 
        if join.get('result') == "criminalCharge":
            for t in trialinfo:
                    if t.get('id') in join.get('targets'):
                       for p in offencelist:
                        if p.get('offenceid') in join.get('targets'):
                            t["offence"] = p.get('offenceCategory')
                            t["offenceSubcategory"] = p.get('offenceSubcategory')
                       for q in verdictlist:
                        if q.get('verdictid') in join.get('targets'):
                            t["verdict"] = q.get('verdict')
    return trialinfo

##### main

def gettrialsinfo(dates,where):
    details = list()
    tlist = getbaileytrials(dates,where)
    for i in tlist:
        x = gettrialdetails(i)
        details.extend(x)
    return details
    
def createtrialscsv(details):
    with open('enfield-trials.csv', 'w', newline='') as csvfile:
        fieldnames = ['trial', 'place', 'year', 'id', 'given', 'surname', 'gender', 'age', 'offence', 'offenceSubcategory', 'verdict']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in details:
            writer.writerow(i)
            # print("written")

def maketrialscsv(dates,where):
    details = gettrialsinfo(dates,where)
    createtrialscsv(details)
    return details
        
############ data

enfield=["18190113","18671216"] 
 
test = ["18391125","18391216"]
twentyyeardates = ["18190113","18391216"]
tenyrdates = ["18240114","18341205"]
rdates = ["18360104","18761211"]
where = "enfield"

trials = maketrialscsv(twentyyeardates,where)
outdata = open('trials.json', 'w')
json.dump(trials, outdata, indent=4)

y1819 = ["18190113","18191201"] 
y1820 = ["18200416","18201206"] 
y1821 = ["18210110","18211205"] 
y1822 = ["18220109","18221204"] 
y1823 = ["18230115","18231203"] 
y1824 = ["18240114","18241202"] 
y1825 = ["18250113","18251208"] 
y1826 = ["18260112","18261207"] 
y1827 = ["18270111","18271206"] 
y1828 = ["18280110","18281204"] 
y1829 = ["18290115","18291203"]
y1830 = ["18300114","18301209"] 
y1831 = ["18310106","18311201"]
y1832 = ["18320105","18321129"]
y1833 = ["18330103","18331128"]
y1834 = ["18340102","18341205"]
y1835 = ["18350105","18351214"]
y1836 = ["18360104","18361212"]
y1837 = ["18370102","18371211"]
y1838 = ["18380101","18381231"]
y1839 = ["18390204","18391216"]
test = ["18200918","18200918"]