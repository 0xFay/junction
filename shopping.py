import time
import threading
import requests
import speech_recognition as sr
import pyaudio,wave
import os
import bs4

class voice:
    def __init__(self):
        self.WAVE_OUTPUT_FILENAME = "demand.wav"
    def record_demand(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 16000
        RECORD_SECONDS = 5
        

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

        print("[+]please speak out your demand...")

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("record finish...")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


    def demand(self):
        r = sr.Recognizer()
        h = sr.AudioFile(self.WAVE_OUTPUT_FILENAME)
        with h as source:
            r.adjust_for_ambient_noise(source,duration=0.2)
            audio = r.record(source)

        result = r.recognize_google(audio, language="cmn-Hans-CN", show_all=True)
        print(result)
        print('\n')
        os.remove(self.WAVE_OUTPUT_FILENAME)

        for t in range(0,len(result['alternative'])):
            if '买' in result['alternative'][t]['transcript']:
                if '洗衣液' in result['alternative'][0]['transcript']:
                    print('[+]洗衣液商品清单:>>\n')
                    for i in GoodsList:
                        if i['goodstype'] == "Laundry detergent":
                            print(i)
                    break    
            
                elif '纸巾' in result['alternative'][0]['transcript']:
                    print('[+]纸巾商品清单:>>\n')
                    for i in GoodsList:
                        if i['goodstype'] == "Paper":
                            print(i)
                    break    
                    
                else:
                    print('unknown demand')
                    break           
            else:
                print('please try again')

    def getkeyword(self):
        r = sr.Recognizer()
        h = sr.AudioFile(self.WAVE_OUTPUT_FILENAME)
        with h as source:
            r.adjust_for_ambient_noise(source,duration=0.2)
            audio = r.record(source)

        result = r.recognize_google(audio, language="cmn-Hans-CN", show_all=True)
        print('your demand is :>>')
        print(result['alternative'][0]['transcript'])
        print('\n')

        os.remove(self.WAVE_OUTPUT_FILENAME)

        return result['alternative'][0]['transcript']
    
    def choosetobuy(self,user):
        r = sr.Recognizer()
        h = sr.AudioFile(self.WAVE_OUTPUT_FILENAME)
        with h as source:
            r.adjust_for_ambient_noise(source,duration=0.2)
            audio = r.record(source)

        result = r.recognize_google(audio, language="cmn-Hans-CN", show_all=True)
        #print(result)

        os.remove(self.WAVE_OUTPUT_FILENAME)

        for t in range(0,len(result['alternative'])):
            if '1' or '一' in result['alternative'][t]['transcript']:
                user.buy(GoodsList[final[0][2]])
                break
            if '2' or '二' in result['alternative'][t]['transcript']:
                user.buy(GoodsList[final[1][2]])
                break
            else:
                print('please try again')



class User:
    def __init__(self):
        self.wishlist = []
        self.rebuygoods = []
    
    def buy(self,parameter):

        for i in self.rebuygoods:
            if i['name'] == parameter['name']:
                i['rebuytime'] =  time.time() - i['lastbuy']
                i['lastbuy'] = time.time()
                #print(self.rebuygoods)
                joinwishlist_watch = threading.Thread(target=self.joinwishlist,args=(parameter,i['lastbuy']))
                joinwishlist_watch.start()
                return
        
        parameter['lastbuy'] = time.time()
        self.rebuygoods.append(parameter)
        #print(self.rebuygoods)
        print('buy it successfully')
        joinwishlist_watch = threading.Thread(target=self.joinwishlist,args=(parameter,parameter['lastbuy']))
        joinwishlist_watch.start()
        
    def joinwishlist(self,parameter,lastbuy):
        while True:
            time_to_buy = time.time() - lastbuy
            if parameter['rebuytime'] - time_to_buy <= 10:
                self.wishlist.append(parameter['name'])
                print('join wish list successfully')
                break

class Goods:
    def __init__(self,goodstype,name,price,rebuytime,rebuyrate,Phosphorus_content,weight,url):
        self.goodstype = goodstype
        self.name = name
        self.price = price
        self.rebuytime = rebuytime
        self.rebuyrate = rebuyrate
        self.Phosphorus_content = Phosphorus_content
        self.url = url
        
        
    def parameter(self):
        self.parameters = {
            'goodstype':self.goodstype,
            'name':self.name,
            'price':self.price,
            'rebuytime':self.rebuytime,
            'rebuyrate':self.rebuyrate,
            'Phosphorus content':self.Phosphorus_content,
            'url':self.url
            }
        return self.parameters

class analizy: 
    def __init__(self):
        self.positive_words = ['好','牛逼','不错','棒','强','出色','喜欢','顶']
        self.negative_words = ['坏','差','烂','垃圾','慢']

    def reviews_device(self,parameter,keyword,number):
        url = parameter['url']
        #r = requests.get(url)
        #爬虫爬取评论对比字典,区分好坏评价,等同于大数据分析
        positive_reviews = [1,2,3,4]
        negative_reviews = [1,2]
        positive_rate = len(positive_reviews)/(len(positive_reviews)+len(negative_reviews))
        return (parameter['name'],positive_rate,number)
    
    def sort(self,arg):
        for i in range(0,len(arg)-1):
            if arg[i][1] < arg[i+1][1]:
                arg[i],arg[i-1] = arg[i-1],arg[i]
        return arg

        

if __name__ == "__main__":
    global GoodsList
    GoodsList = []

    Walch = Goods("Laundry detergent","Walch",34.9,50,0.5,0.1,4.26,'https://xxx.xx')
    GoodsList.append(Walch.parameter())
    Tide = Goods("Laundry detergent","Tide",9.9,40,0.6,0.09,1.36,'https://xxx.xxx')
    GoodsList.append(Tide.parameter())
    
    fay = User()

    voice_try = voice()
    voice_try.record_demand()
    voice_try.demand()
    
    voice_try.record_demand()
    keyword = voice_try.getkeyword()

    ana = analizy()
    
    sort_array = []
    for o in range(0,len(GoodsList)):
        sort_array.append(ana.reviews_device(GoodsList[o],keyword,o))

    final = ana.sort(sort_array)
    print('Goods list:>>')
    print(final)

    voice_try.record_demand()
    voice_try.choosetobuy(fay)

    
    

    #print(Walch.parameter())
    #fay.buy(Walch.parameter())


