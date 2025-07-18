
limit = 10
pass_list = list('a' * 100)

for i in range(0, len(pass_list), limit):
    print("[+] batch:", i)

    # batch = pass_list[i:i + limit]
    # for j, password in enumerate(batch):
    #     print(i+j)
    for j in range(i,i + limit):
        print(j)
