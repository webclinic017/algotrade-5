from os import listdir, system, remove, path, mkdir

def RefreshData():
    if not path.exists("./logs/Data"):
        mkdir("./logs/Data")

    if not path.exists("./logs/KiteData"):
        mkdir("./logs/KiteData")

    system("aws s3 sync ./logs/ s3://www.101logs.com.in/")
    system("aws s3api put-object-acl --bucket www.101logs.com.in --key index.html --acl public-read")

    files = listdir("./logs/Data")

    #[system(f"aws s3 cp ./logs/Data/{fil} s3://www.101logs.com.in/misc/") for fil in files]

    [remove(f"./logs/Data/{fil}") for fil in files if ("budget" not in fil)]

    files = listdir("./logs/KiteData")

    #[system(f"aws s3 cp ./logs/KiteData/{fil} s3://www.101logs.com.in/ticks/") for fil in files]

    [remove(f"./logs/KiteData/{fil}") for fil in files]