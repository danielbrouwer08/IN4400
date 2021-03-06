#Python script to analyze the data collected by the datacollector script

import urllib, sys, jsonpickle, time, os
import simplejson as json
from time import sleep
from geoip import geolite2
url = "https://blockchain.info/unconfirmed-transactions?format=json"
transactions = [] #variable that holds all unique transactions
transAmount=0 #variable that holds the total amount of transactions
sources = [] #variable that holds all unique sources
sourcesAmount=0 #variable that holds the total amount of sources

prevTransactions = [] #hold previous transactions
delay = 0.5 #delay in seconds between every json request
iterations = 86400 #remember the amount of time is approximatelly iterations*delay
saveInterval = 200 #after how many iterations you want me to save the intermediate data? For accuracy keep this as low as possible (will be more cpu and io intensive)

sourcesObj=[]
transactionsObj=[]

#---<CLASSES>---#

class address: #class representing a bitcoin address

    def __init__(self,address,value):
        self.address = address  #the address
        self.value = value #the amount of money that is transfered 
    def __str__(self): #to string method
        return "Address: " + self.address + " ;#Value: %d" % (self.value)


class transaction: #class transfer representing a transaction
    
    def __init__(self,t_hash,timestamp,ip,sources,destinations):
        self.t_hash = t_hash #hash of th transaction
        self.timestamp = timestamp #time stamp of the transaction
        self.ip = ip #ip address of the transaction
        self.sources = sources #list of sources
        self.destinations = destinations #list of destinations
        self.country = countryFromIP(ip)
    def __str__(self):
        return "hash: " + self.t_hash

class source: #class representing a source containing the address and all the transactions from this source
    
    def __init__(self,srcaddress,amount,transactionsAmount):
        self.address = srcaddress #the address
        self.amount  = amount #the amount that is transfered
        self.transactions = transactionsAmount #the transactions amount

    def __str__(self):
        return "address: " + self.srcaddress.address + "; #transactions: %d" % (len(self.transactions))

#---</CLASSES>---#

#---<FUNCTIONS>---#

def sumTransactionsPerSource(sources,uniqueSources):
    sourcesNew=[]
    for x, usrc in enumerate(uniqueSources):
        sourcesNew.append(source(usrc.address,0,0))#create a source
        for y, src in enumerate(sources):
            if src.address==usrc.address: #if the same
		print "\rsumming transaction.. x=%d,y=%d" % (x,y),
                sourcesNew[x].amount+=src.amount #sum amount of money
                sourcesNew[x].transactions+=1 #sum amount of transactions
                
    return sourcesNew


def findUniqueSources(sources): #find all unique sourcces
    sourcesNew=[] #temp list to store all the source objects
    for x, src in enumerate(sources):
        if (containsSource(src,sourcesNew)==False): #if the source is not already in the new list
        	print "\rNew unique source added.. no.%d" % x,
		sourcesNew.append(src) #append it to the list


    return sourcesNew

def containsSource(src,sources):
    for usrc in sources:
        if usrc.address==src.address:
            return True

    return False

def getFromFile():
    global transAmount
    global sourcesAmount
    global sources
    global transactions
    for subdir, dirs, files in os.walk('./data/'):
        for file in files:
            filepath = subdir + os.sep + file #path of file
            if(file[0]=='t'): #if the first letter is an t->it is a transaction
                try:
                    tmp=open(filepath,"r") #open the file for reading
                    #print "adding transaction"
                
                    translist=json.loads(tmp.read())
                    for trans in translist:
                        transactions.append(trans) #store all transactions
                        transAmount+=1
                
                    tmp.close() #close the file
                    #print transactions[0]
                except Exception as e:
                    pass
                    #print "hmmm... this is not good, I failed to load the JSON file for a transaction maybe the JSON file is corrupted?"
            
            elif(file[0]=='s'): #if the first letter is an s-> it is a source
                #print "adding source"
                tmp=open(filepath,"r") #open the file for reading

                sourcelist=json.loads(tmp.read())
                for src in sourcelist:
                    try:
                        addr = src["srcaddress"]["address"]
                        value = src["srcaddress"]["value"]
                        amount  = len(src["transactions"])  

                        sources.append(source(addr,value,amount)) #make source object and append it to the list
                        sourcesAmount+=1
                        tmp.close() #close the file
                
                    except Exception as e:
                        pass
                        #print "well.. something went wrong at converting json source to an object"

            print "Sources: %d    Transactions: %d" % (sourcesAmount,transAmount)
                    
            #filepath = subdir + os.sep + file
            #print (filepath)


def averageTransactionAmount(sources): #calculate the average transaction amount
    totalValue=0
    totalTrans=0
    for src in sources:
        #print "amount: % d  transactions: %d",(src.amount,src.transactions)
        totalValue+=src.amount
        totalTrans+=src.transactions
        print "\rTotal value: " + str(totalValue/100000000.0) + "Total trans: " + str(totalTrans),
    return totalValue/float(100000000.0)/totalTrans



def averageTransactions(sources): #calculate the average transaction amount
    totalTrans=0
    totalSrcs=0
    for src in sources:
        #print "amount: % d  transactions: %d",(src.amount,src.transactions)
        totalSrcs+=1
        totalTrans+=src.transactions
        
    return totalTrans/totalSrcs



def sortOnTransactionCount(sources):
    return sorted(sources, key=lambda source: source.transactions,reverse=True)


getFromFile() #retrieve all dat
print "finding unique transactions and summing them..."
sourcesUniqueSum=sumTransactionsPerSource(sources,findUniqueSources(sources)) #get all unique sources with there transactions amount summed
print "calculating average transaction amount.."
averageTrans=averageTransactionAmount(sourcesUniqueSum) #get the average transaction amount
print "calculating average transactions.."
averageTransactions=averageTransactions(sourcesUniqueSum)
print "sorting the sources.."
sortedSources=sortOnTransactionCount(sourcesUniqueSum)


#write the results to file:
file = open("results.txt", "w")
data="Average transaction amount: " + str(averageTrans) + " = " + str(averageTrans*893.3) +  " USD\n"
data+= "Average transactions: " + str(averageTransactions) + "\n\n"
file.write(data)

for x in range(0,50): #print 50 best sources and store them in a variable
    print("Address: " + sortedSources[x].address + " transactions: %d total: %d" % (sortedSources[x].transactions,sortedSources[x].amount))
    data="Address: " + sortedSources[x].address + " transactions: " + str(sortedSources[x].transactions) + " total: " + str(sortedSources[x].amount)+"\n"
    file.write(data)

file.close() #close the file writer

print "Average transaction amount: %f BTC = %d USD" % (averageTrans,averageTrans*893.3)
print "Average transactions: %d" % (averageTransactions)


#---</FUNCTIONS>---#

