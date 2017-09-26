with open("doc2vec.txt") as f:
    content = f.readlines()
    numberOfVectors = 0
    dimensions = 0
    inputArr = []
    docIdArr = []
    
    for i in range(len(content)):
        if i == 0:
            numberOfVectors = content[i].split(" ")[0]
            dimensions = content[i].split(" ")[1] 
        else:
            input = []
            data = content[i].split(" ")
            docIdArr.append(data[0])

            for j in range(int(dimensions)):
                input.append(float(data[j+1]))
            inputArr.append(input)
            
    print(inputArr)


with open("node2vec.txt") as f:
    content = f.readlines()
    numberOfVectors = 0
    dimensions = 0
    outputArr = []
    docIdArrNode2Vec = []
    
    for i in range(len(content)):
        if i == 0:
            numberOfVectors = content[i].split(" ")[0]
            dimensions = content[i].split(" ")[1] 
        else:
            output = []
            data = content[i].split(" ")
            docIdArrNode2Vec.append(data[0])

            for j in range(int(dimensions)):
                output.append(float(data[j+1]))
            outputArr.append(output)
            
    print(outputArr)
    
