nums=[1,2,3,4,5,1]
print(len(nums))
for i in range(len(nums)):
    for j in range(i+1,len(nums)):
        if nums[i]==nums[j]:
            print(True)
        else:
            print(False) 