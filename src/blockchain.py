import urllib, json, sys
from time import sleep
url = "https://blockchain.info/unconfirmed-transactions?format=json"
transactions = [] #variable that holds all unique transactions
delay = 0.5 #delay in seconds between every json request
iterations = 120 #remember the amount of time is approximatelly iterations*delay
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
    def __str__(self):
        return "hash: " + self.t_hash

class source: #class representing a source containing the address and all the transactions from this source
    
    def __init__(self,srcaddress,transactions):
        self.srcaddress = srcaddress #the address
        self.transactions = transactions #the transactions that were initiated from this source

    def __str__(self):
        return "address: " + self.srcaddress.address + "; #transactions: %d" % (len(self.transactions))

#---</CLASSES>---#

#---<FUNCTIONS>---#

def findHash(transactions,t_hash): #find "hash" in "transactions"
    for index, trans in enumerate(transactions): #loop over all transactions
        if trans.t_hash == t_hash:
            return index #return the index of the transaction if hash is found
    return None #return None if hash is not found 

def findTransactionsBySource(transactions,address): #find in the list of transactions all transactions a specific address has made
    transBySource=[] #temp list to store the transactions specific to an address
    for x, trans in enumerate(transactions): #loop over all transaction
        for y, source in enumerate(transactions[x].sources): #loop over all source addresses
            if source.address == address: #if address is in sources
                transBySource.append(trans) #append the transaction to the list
                break #break the first for loop

    return transBySource

def findSource(sources,source):
    for index, src in enumerate(sources):
        if src.address == source.address:
            return index
    
    return None


def findUniqueSourceAddresses(transactions): #find all the unique source addresses
    sourceAddrs=[] #temp list to store the source addresses
    for x, trans in enumerate(transactions):
        for y, src in enumerate(transactions[x].sources):
           tmp=findSource(sourceAddrs,src) #check if source is already in sources list
           
           if tmp is None: #if the source is not already in the list
               sourceAddrs.append(src) #add it!
    return sourceAddrs #return the list with unique source addresses

def findUniqueSources(transactions,sourceAddresses): #combine every sourceAddress with a transaction
    sources=[] #temp list to store all the source objects
    for x, src in enumerate(sourceAddresses):
        sources.append(source(src,findTransactionsBySource(transactions,src.address))) #find all the transactions initiated from this sourceaddress, make a source object and store it

    return sources
def getJson(): #get all json data (50 entries)
    response = urllib.urlopen(url) #retrieve the response
    data = json.loads(response.read()) #interpret the response as JSON
    amount = len(data['txs']) #amount of data received
        
    for x in range(0, amount): #loop over all the data entries received
        t_hash=(data['txs'][x]['hash']) #retrieve the hash of the transaction
        t_index=findHash(transactions,t_hash) #check if hash is already in the transactions list
        timestamp=(data['txs'][x]['time']) #retrieve the timestamp
        ip=(data['txs'][x]['relayed_by']) #retrieve the ip

        if t_index is None: #if hash is not already in the transactions list
            sys.stdout.flush() #flush output
            print ("\rTransaction count: %d" % (len(transactions))),
            sources=[] #temp list to store the sources into
            destinations=[] #temp list to store the destinations into
            for y in range(0,len(data['txs'][x]['inputs'])): #loop over all input bitcoin addresses
                sources.append(address(data['txs'][x]['inputs'][y]['prev_out']['addr'],data['txs'][x]['inputs'][y]['prev_out']['value'])) #make a new address object and store it into the sources
            
            for y in range(0,len(data['txs'][x]['out'])): #loop over all output bitcoin addresses
                destinations.append(address(data['txs'][x]['out'][y]['addr'],data['txs'][x]['out'][y]['value'])) #make a new address object and store it into the destinations list
            
            transactions.append(transaction(t_hash,timestamp,ip,sources,destinations)) #add the transaction to the list

        #else:
            #print("\rTransaction count: %d ; Transaction already saved" % (len(transactions))),


for x in range(0,iterations): #iterate over the getJson function
    getJson()
    sleep(delay) #sleep for "delay" seconds

#srcAddrs=findUniqueSourceAddresses(transactions) #get all the unique addresses

sources=findUniqueSources(transactions,findUniqueSourceAddresses(transactions))#make a list of all unique sources (each source has an address and corresponding transaction)

#print "transactions"                
#for x in range(0, len(transactions)):
#    print(transactions[x])

#print "sourceaddrs"
#for x in range(0, len(srcAddrs)):
#    print(srcAddrs[x])

print "sources"
for x in range(0, len(sources)):
    print(sources[x])

#---</FUNCTIONS>---#

