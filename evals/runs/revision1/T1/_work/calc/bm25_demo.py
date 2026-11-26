from math import log
N=4
avgdl=150
k1=1.2
b=0.75
idf=log(1+(N-3+0.5)/(3+0.5))
def contribution(tf,dl):
    return idf*tf*(k1+1)/(tf+k1*(1-b+b*dl/avgdl))
print(f"IDF(df=3,N=4)={idf:.6f}")
print(f"IDF(df=4,N=4)={log(1+(N-4+0.5)/(4+0.5)):.6f}")
for label,tf,dl in [('short',1,50),('repeat',3,150),('long',3,300)]:
    print(f"{label}: tf={tf}, length={dl}, contribution={contribution(tf,dl):.6f}")
for tf in [1,2,10,100]:
    print(f"fixed_length: tf={tf}, factor={tf*(k1+1)/(tf+k1):.6f}")
print(f"fixed_length_upper_bound={k1+1:.6f}")
