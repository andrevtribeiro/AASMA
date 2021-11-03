import numpy as np
import matplotlib.pyplot as plt
import os
# Events
# [Winter,Spring,Summer,Autumn,Rain/Storm,HeatWave,
# Christmas/NewYear,Easter,Carnaval,Valentine,Halloween,Disease,Euro Rate Increase,
# Euro Rate Decrease]
events_index={'Winter':0,'Spring':1,'Summer':2,'Autumn':3,'Rain':4,'HeatWave':5,'Christmas/NewYear':6,
'Easter':7,'Carnaval':8,'Valentine':9,'Halloween':10,'Disease':11,'Euro Rate Increase':12,'Euro Rate Decrease':13}

temperatures=[11,11,12,14,16,19,20,24,23,18,14,12]
months_days=[31,29,31,30,31,30,31,31,30,31,30,31]

rain=[0.3,0.3,0.3,0.4,0.2,0.1,0.05,0.05,0.1,0.2,0.3,0.4]


winter={12:[21,31],1:[1,31],2:[1,31],3:[1,20]}
spring={3:[21,31],4:[1,31],5:[1,31],6:[1,20]}
summer={6:[21,31],7:[1,31],8:[1,31],9:[1,20]}
autumn={9:[21,31],10:[1,31],11:[1,31],12:[1,20]}

disease=0
euro=0
euro_increase=False
euro_decrease=False

gelado=[0.1,0.25,0.55,0.35,0.5,1.4,1,1,1,1,1,0.5,1.25,0.7]
cha=[0.6,0.3,0.05,0.2,1.2,0.5,1.2,1,1,1,1,1.2,1.1,0.9]

items=[gelado,cha]

clients=100
last_rain=False

year=2010
years=10

sales_list=[[] for i in range(len(items))]
days=[i+1 for i in range(366*years)]

mediumDaySales=[0 for i in range(len(items))]
def getSales(item,events):
    global clients
    sales=0
    p=1
    for i,j in zip(item,events):
        if j==1:
            p*=i
    if p<0:
        p=0
    if p>1:
        p=1
    for client in range(int(clients*p)):
        quantity=int(np.random.normal(200,50))
        if quantity<10:
            quantity=10
        sales+=quantity
    return sales

    

def checkDisease():
    global disease
    if disease==0:     
        disease=np.random.rand()
        if disease>0.9:
            disease=int(np.random.normal(50,10))
            if disease<30:
                disease=30
        else:
            disease=0
            return False
    disease=disease-1
    return True

def checkEuro():
    global euro,euro_increase,euro_decrease
    if euro==0:     
        euro=np.random.rand()
        if euro>0.9:
            euro_increase=True
            euro=int(np.random.normal(120,10))
            if euro<100:
                euro=100
        elif euro<0.1:
            euro_decrease=True
            euro=int(np.random.normal(120,10))
            if euro<100:
                euro=100
        else:
            euro=0
            euro_increase=False
            euro_decrease=False
            return
    euro=euro-1
    
    

def checkRain(m):
    global rain,last_rain
    p=rain[m]
    if last_rain:
        p+=0.3
    if p>1:
        p=1
    if np.random.rand()>(1-p):
        last_rain=True
        return True
    last_rain=False
    return False

def season(m,d,dic):
    if m not in dic:
        return False
    l=dic[m]
    if d>=l[0] and d<=l[1]:
        return True
    return False


f=open("dataset.txt", "w")
for y in range(years):
    for item in items:
        sales_year=[[] for i in items]
        events_year=[[] for i in items]
    for m in range(len(months_days)):
        for d in range(months_days[m]):
            events=[0 for i in range(14)]
            temperature=np.random.normal(temperatures[m],2)
            if season(m+1,d+1,winter):
                events[events_index['Winter']]=1
                if m+1==12 and d>=20 and d<=1:
                    events[events_index['Christmas/NewYear']]=1
                elif m+1==2 and d>=1 and d<=14:
                    events[events_index['Valentine']]=1
                if m+1==2:
                    events[events_index['Carnaval']]=1
            elif season(m+1,d+1,spring):
                events[events_index['Spring']]=1
                if m+1==3 and m+1==4:
                    events[events_index['Easter']]=1
            elif season(m+1,d+1,summer):
                events[events_index['Summer']]=1
            elif season(m+1,d+1,autumn):
                events[events_index['Autumn']]=1
                if m+1==10:
                    events[events_index['Halloween']]=1
            if checkDisease():
                events[events_index['Disease']]=1
            if temperature>25:
                events[events_index['HeatWave']]=1
            if checkRain(m):
                events[events_index['Rain']]=1
            checkEuro()
            if euro_increase:
                events[events_index['Euro Rate Increase']]=1
            elif euro_decrease:
                events[events_index['Euro Rate Decrease']]=1
            for i in range(len(items)):
                sales_year[i]+=[getSales(items[i],events)]
                events_year[i]+=[events]
                sales_list[i]+=[sales_year[i][-1]]
      
    for i in range(len(items)):
        alpha=sum(sales_year[i])/len(sales_year[i])
        mediumDaySales[i]+=alpha
        for day in range(len(sales_year[i])):
            f.write(str([i]+events_year[i][day]))
            v=sales_year[i][day]
            classe=0
            if v>alpha:
                classe=3+3*(v-alpha)/v
            elif v<alpha:
                classe=3-3*(alpha-v)/alpha
            else:
                classe=3
            f.write(" %d\n" %(round(classe)))
f.close()


with open('avgDaySales.txt','w') as f:
    a=round(mediumDaySales[0]/years)
    b=round(mediumDaySales[1]/years)
    f.write(("%d\n%d" %(a,b)))
fig, (gelado_ax, cha_ax) = plt.subplots(1, 2, figsize=(20,7))

gelado_ax.set_title('Gelado')
gelado_ax.plot(days,sales_list[0])
gelado_ax.set_ylabel('Sales')
gelado_ax.set_xlabel('Days')

cha_ax.set_title('Cha')
cha_ax.plot(days,sales_list[1])
cha_ax.set_ylabel('Sales')
cha_ax.set_xlabel('Days')

plt.savefig('dataset.png')
plt.close()

if os.path.exists("NN_model.h5"):
  os.remove("NN_model.h5")

if os.path.exists("multi_layer_best.h5"):
  os.remove("multi_layer_best.h5")


