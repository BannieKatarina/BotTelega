F=open('17-1.txt')
data=F.readlines()
l=[]
k=0
max=-10001
for i in range(len(data)-1):
    l.append(data[i][:])
l=list(map(int,l))
for i in range(len(l)-1):
    if (l[i]%9==0 and l[i+1]%9!=0 and l[i+1]%8==3) or (l[i+1]%9==0 and l[i]%9!=0 and l[i]%8==3):
        k+=1
        if l[i]>max:
            max=l[i]
        if l[i+1]>max:
            max=l[i+1]
print(k, max)