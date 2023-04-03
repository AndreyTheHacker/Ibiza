# By NDRAEY

import aiohttp as aih
import asyncio
import sys
import json
import random
import aiofiles

works = []

async def download(session, url, name):
    #print("Starting download "+name)
    if name in works:
        name = name.split(".")[0]+str(random.randint(88888,777777))+"."+name.split(".")[-1]
    works.append(name)
    chunksize = 8192
    await asyncio.sleep(0.5)
    async with session.get(url) as resp:
        if resp.status == 200:
            f = await aiofiles.open(name, mode='wb')
            load = 0
            while True:
                loaded = (load/(1024**2))
                print("\033["+str(works.index(name))+";0"+"H", end='')
                print("%-30s => %.3fMB"%(name, loaded), end='\r')
                #print(works.index(name))
                chunk = await resp.content.read(chunksize)
                if not chunk: break
                await f.write(chunk)
                load += chunksize
            await f.close()
            works.remove(name)
            #print("\033[2J")
            print(" "*38, end='')
            #print("Download of "+name+" OKAY!")

async def getrawdata(query):
    async with aih.ClientSession() as ses:
        async with ses.get("https://tenor.com/search/"+query+"-gifs") as resp:
            return await resp.text()

async def getJSON(query):
    e = await getrawdata(query)
    e=e[e.find("<script id=\"store-cache\" type=\"text/x-cache\" nonce="):]
    e = json.loads(e[e.find("{"):e.find("</script>")])
    return e

async def geturls(query):
    e = await getrawdata(query)
    e=e[e.find("<script id=\"store-cache\" type=\"text/x-cache\" nonce="):]
    e = json.loads(e[e.find("{"):e.find("</script>")])['gifs']['search']
    e = e[list(e.keys())[0]]['results']
    urls = []
    for i in e:
        urls.append(i['media'][0]['gif']['url'])
    return urls

async def main():
    # TODO: Argparser, download mp4 files (they exists)

    arg = ""
    if len(sys.argv[1:])==0:
        arg = input("Query> ")
    else:
        arg = sys.argv[1]
    
    urls = await geturls(arg)
    print("=====[Gotta download "+str(len(urls))+" GIFs!]=====")
    
    async with aih.ClientSession() as session:
        print("Getting ready...")
        print("\033[2J")

        for i in range(len(urls)//8):
            print("Downloading part", i)
            tasks = []
            for url in urls[i*8:(i+1)*8]:
                tasks.append(asyncio.ensure_future(download(session, url, url.split("/")[-1])))

            result = await asyncio.gather(*tasks)

asyncio.run(main())
