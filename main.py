#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Google Inc.
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from google.appengine.ext import webapp
import logging,time,os,jinja2,ast,json,yaml,webapp2
from google.appengine.api import users
from datetime import datetime,timedelta
from google.appengine.ext import ndb
from baseHandler import BaseHandler
from models import Farmdb,Tempdb,DayTempdb,Notificationdb,Changedb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape','jinja2.ext.loopcontrols'],
    autoescape=True)

index = JINJA_ENVIRONMENT.get_template('/templates/index.html')
farm = JINJA_ENVIRONMENT.get_template('/templates/farm.html')
configfarm = JINJA_ENVIRONMENT.get_template('/templates/configfarm.html')
login=JINJA_ENVIRONMENT.get_template('/templates/login.html')
createfarm=JINJA_ENVIRONMENT.get_template('/templates/create-farm.html')
regiserror=JINJA_ENVIRONMENT.get_template('/templates/regiserror.html')
chart=JINJA_ENVIRONMENT.get_template('/templates/chart.html')
repassword=JINJA_ENVIRONMENT.get_template('/templates/repassword.html')
adminrepassword=JINJA_ENVIRONMENT.get_template('/templates/adminrepassword.html')
search=JINJA_ENVIRONMENT.get_template('/templates/search.html')





def createId(day):
    #2017-04-02 05:34
    return time.strptime(day,'%Y-%m-%d %H:%M')

def randomId(data,num=0):
    timePublic= time.localtime()
    sec=str(timePublic.tm_sec)
    if len(str(sec))==1:
        sec ="0"+sec
    timesave=str(timePublic.tm_hour+7)+str(timePublic.tm_min)+sec
    getday = datetime.utcnow()
    year = str(getday.strftime("%Y"))
    month = str(getday.strftime("%m"))
    day = str(getday.strftime("%d"))
    if data != 'f':
        return data+str(year+month+day+timesave)+str(num)
    else:
        return data+str(year+month+day+timesave)
def user_required(handler):
  def check_login(self, *args, **kwargs):
    auth = self.auth
    if not auth.get_user_by_session():
      self.redirect(self.uri_for('login'), abort=True)
    else:
      return handler(self, *args, **kwargs)

  return check_login

def getFarm(self,start=0,limit=10):
    try:
        user = self['auth_ids'][0]                                               #size,first
        Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==user).fetch(offset=start,limit=limit)
    except Exception as e:
        return "errorDB"
    return Farmquery

def getNotification(self,start=0,limit=10):
    try:
        user = self['auth_ids'][0]                                               #size,first
        Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==user).fetch(offset=start,limit=limit)
    except Exception as e:
        return "errorDB"
    return Notificationquery

class Getnoti(BaseHandler):
    def post(self):
        self.response.write(getNotification(self.user_info))
        # return(getNotification(self.user_info))
        # return

def getAllFarm(self):
    try:
        user = self['auth_ids'][0]
        Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==user).fetch()
    except Exception as e:
        return "errorDB"
    return Farmquery


class Createfarm(BaseHandler):
    @user_required
    def get(self):
        user = self.user_info
        try:
            farm=Farmdb.query().filter(Farmdb.user==self.user_info['auth_ids'][0])
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        
        count=0
        for i in farm:
            count +=1
        count +=1
        params={"product_id":count,"user":user,"type":"create"}
        self.response.write(createfarm.render(params))
    @user_required
    def post(self):
        data = self.request
        user=self.user_info['auth_ids'][0]
        nameFarm=data.get('nameFarm')
        numberCrayfish=data.get('numberCrayfish')
        floor=int(data.get('floor'))
        wide=data.get('wide')
        timeEatDay=data.get('timeEatDay')
        temp=data.get('temp')
        macPi=data.get('macPi')
        timeWater=data.get('timeWater')
        idFarm=randomId('f')
        checkNameFarm=Farmdb().query().filter(Farmdb.user==self.user_info['auth_ids'][0],Farmdb.nameFarm==nameFarm).fetch()
        if checkNameFarm:
            self.redirect('/register?message=haveNameFarm')
            return
        listIdArduino=[]
        for i in range(floor):
            listIdArduino.append(randomId('a',i))
        farm=Farmdb()
        farm.id=idFarm
        farm.nameFarm=nameFarm
        farm.numberCrayfish=int(numberCrayfish)
        farm.floor=int(floor)
        farm.wide= int(wide)
        farm.timeEatDay= int(timeEatDay)
        farm.temp = int(temp)
        farm.user = user
        farm.macPi= macPi
        farm.idArduino = listIdArduino
        farm.timeWater = int(timeWater)
        farm.put()
        try:
            checkChange = Changedb().query().filter(Changedb.macPi==macPi).fetch()
            # add notification
            notification=Notificationdb()
            notification.user=user
            notification.idFarm=idFarm
            notification.put()
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        
        if len(checkChange) ==0:
            change=Changedb()
            change.macPi=macPi
            change.put()
        self.redirect('/register?message=farmsuccess')

class Farm(BaseHandler):
    @user_required
    def get(self, *args, **kwargs):
        listFarm=[]
        Farmquery=getFarm(self.user_info)
        FarmqueryAll =getAllFarm(self.user_info)
        if Farmquery=="errorDB":
            self.redirect('/register?message=errorDB')
            return
        try:
            # Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0]).fetch()
            Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0]).fetch()
            
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        
        count=1
        for i in Farmquery:
            listFarm.append(count)
            count+=1
        
        product_id = kwargs['product_id']
        user = self.user_info
        number= int(kwargs['product_id'])-1
        
        time = datetime.now()
        time += timedelta(hours=7)
        calTime=(float(Notificationquery[number].countdownFeeder)/60)/60
        mod=(calTime%1)
        koy=calTime-mod
        lastMod = (mod*60)/100
        result = koy+lastMod
        showTime= "{:.02f}".format(result)

        listDay=[]
        try:
            # self.response.write(number)
            # return
            DayTempquery=DayTempdb.query().order(DayTempdb.day).filter(DayTempdb.idFarm==FarmqueryAll[number].id).fetch()
            
            if len(DayTempquery)==0:
                Tempquery = Tempdb.query().order(Tempdb.time).filter(Tempdb.idFarm==FarmqueryAll[number].id).fetch()
            else:
                Tempquery = Tempdb.query().order(Tempdb.time).filter(Tempdb.idFarm==FarmqueryAll[number].id,Tempdb.day==DayTempquery[-1].day).fetch()
        except Exception as e:

            self.redirect('/register?message=errorDB')
            return

        for i in DayTempquery:
            tempDate=str(i.day.day)+"/"+str(i.day.month)+"/"+str(i.day.year)
            listDay.append(tempDate)
        # temp=[]

        listDay=listDay[::-1]
        hour=None
        tempHour=None
        listTempPerHour=[]
        label=[]
        data=[]
        for i in range(len(Tempquery)):
            testTime=Tempquery[i].time+timedelta(hours=7)
            if i >0 and i != len(Tempquery)-1:
                
                if hour==testTime.hour:
                    listTempPerHour.append(Tempquery[i].temp)
                else:
                    tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                    listTempPerHour=[]
                    listTempPerHour.append(Tempquery[i].temp)
            #last
            elif i == len(Tempquery)-1:
                if hour==testTime.hour:
                    listTempPerHour.append(Tempquery[i].temp)
                    tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                else:
                    if i!=0:
                        tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    else:
                        hour=testTime.hour
                        tempHour=Tempquery[i].temp
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                    tempHour = float("{:.02f}".format(Tempquery[i].temp))
                    # temp.append({'label':str(testTime.hour)+'.00','y':Tempquery[i].temp})
                    label.append(str(testTime.hour)+'.00')
                    data.append(Tempquery[i].temp)
            #first
            else:
                listTempPerHour.append(Tempquery[i].temp)
            hour=testTime.hour
            
            # label="{:d}:{:02d}".format(testTime.hour,Tempquery[i].time.minute)
            # self.response.write(testTime.hour)
            # return
            # temp.append({'label':label,'y':Tempquery[i].temp})

        listArduino = FarmqueryAll[number].idArduino
        params={"product_id":int(product_id),
                "listFarm":listFarm,
                "user":user,
                "type":"farm",
                "content":FarmqueryAll[number],
                "ListNameFarm":Farmquery,
                "Notification":Notificationquery[number],
                'showTime':showTime,
                "listDay":listDay,
                # "temp":temp,
                "listArduino":listArduino,
                "label":label,
                "data":data}
        # self.response.headers['Content-Type'] = 'text/html'
        self.response.write(farm.render(params))
    
class Configfarm(BaseHandler):
    @user_required
    def get(self, *args, **kwargs):
        listFarm=[]
        Farmquery=getFarm(self.user_info)
        allFarm=getAllFarm(self.user_info)
        if Farmquery=="errorDB":
            self.redirect('/register?message=errorDB')
            return
        # try:
        #     Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0]).fetch()
        # except Exception as e:
        #     self.redirect('/register?message=errorDB')
        #     return
        count=1
        for i in Farmquery:
            listFarm.append(count)
            count+=1
        
        product_id = kwargs['product_id']
        user = self.user_info
        number= int(kwargs['product_id'])-1
        listArduino = allFarm[number].idArduino
        
        params={"product_id":int(product_id),
                "listFarm":listFarm,
                "user":user,
                "type":"configfarm",
                "ListNameFarm":Farmquery,
                "content":allFarm[number],
                "listArduino":listArduino}
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(configfarm.render(params))

    def post(self, *args, **kwargs):
        data = self.request
        user=self.user_info['auth_ids'][0]
        name=data.get('nameFarm')
        numberCrayfish=data.get('numberCrayfish')
        floor=data.get('floor')
        wide=data.get('wide')
        timeEatDay=data.get('timeEatDay')
        temp=data.get('temp')
        macPi=data.get('macPi')
        oldmacPi=data.get('oldMac')
        timeWater=data.get('timeWater')
        idFarm=data.get('id')
        idArduino=data.get('idArduino')
        oldFloor=data.get('oldFloor')
        idArduino = ast.literal_eval(idArduino)
        newListIdArduino=[]
        if floor < oldFloor:
            for i in range(int(floor)):
                newListIdArduino.append(idArduino[i])

        elif floor > oldFloor:
            different=int(floor)-int(oldFloor)
            for i in range(different):
                idArduino.append(randomId('a',i))
            newListIdArduino=idArduino
        else:
            newListIdArduino=idArduino
        try:
            farm=Farmdb.query().filter(Farmdb.id==idFarm,Farmdb.user==user)
            change=Changedb().query().filter(Changedb.macPi==oldmacPi)
            getChange=change.get()
            getChange.macPi=macPi
            getChange.change=True
            getChange.put()
            farmget=farm.get()
            farmget.nameFarm=name
            farmget.numberCrayfish=int(numberCrayfish)
            farmget.timeEatDay= int(timeEatDay)
            farmget.temp = int(temp)
            farmget.wide = int(wide)
            farmget.user = user
            farmget.macPi= macPi
            farmget.floor= int(floor)
            farmget.idArduino=newListIdArduino
            farmget.timeWater = int(timeWater)
            farmget.put()
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        list=[]
        for i in farm:
            list.append(i)
        self.redirect('/register?message=updatefarm')

class ChartDay(BaseHandler):
    @user_required
    def get(self, *args, **kwargs):
        Farmquery=getFarm(self.user_info)
        if Farmquery=="errorDB":
            self.redirect('/register?message=errorDB')
            return
        listFarm=[]
        try:
            # Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0]).fetch()
            Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0]).fetch()
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        
        count=1
        for i in Farmquery:
            listFarm.append(count)
            count+=1
        product_id = kwargs['product_id']
        day = kwargs['day']
        month = kwargs['month']
        year = kwargs['year']
        user = self.user_info
        number= int(kwargs['product_id'])-1
        date=createId(str(year)+'-'+str(month)+'-'+str(day)+" "+"00:00")
        dateSave=datetime(date.tm_year,date.tm_mon,date.tm_mday)
        chartFarm=str(day)+"/"+str(month)+"/"+str(year)
        listDay=[]

        try:
            DayTempquery=DayTempdb.query().order(DayTempdb.day).filter(DayTempdb.idFarm==Farmquery[number].id).fetch()
            if len(DayTempquery)==0:
                Tempquery = Tempdb.query().order(Tempdb.time).filter(Tempdb.idFarm==Farmquery[number].id).fetch()
            else:
                Tempquery = Tempdb.query().order(Tempdb.time).filter(Tempdb.idFarm==Farmquery[number].id,Tempdb.day==dateSave).fetch()
        except Exception as e:
            self.redirect('/register?message=errorDB')
            return
        
        for i in DayTempquery:
            tempDate=str(i.day.day)+"/"+str(i.day.month)+"/"+str(i.day.year)
            listDay.append(tempDate)
        temp=[]
        hour=None
        tempHour=None
        listTempPerHour=[]
        label=[]
        data=[]
        for i in range(len(Tempquery)):
            testTime=Tempquery[i].time+timedelta(hours=7)
            if i >0 and i != len(Tempquery)-1:
                
                if hour==testTime.hour:
                    listTempPerHour.append(Tempquery[i].temp)
                else:
                    tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                    listTempPerHour=[]
                    listTempPerHour.append(Tempquery[i].temp)

            #last
            elif i == len(Tempquery)-1:
                if hour==testTime.hour:
                    listTempPerHour.append(Tempquery[i].temp)
                    tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                else:
                    if i!=0:
                        tempHour=sum(listTempPerHour)/(len(listTempPerHour))
                    else:
                        hour=testTime.hour
                        tempHour=Tempquery[i].temp
                    tempHour = float("{:.02f}".format(tempHour))
                    # temp.append({'label':str(hour)+'.00','y':tempHour})
                    label.append(str(hour)+'.00')
                    data.append(tempHour)
                    tempHour = float("{:.02f}".format(Tempquery[i].temp))
                    # temp.append({'label':str(testTime.hour)+'.00','y':Tempquery[i].temp})
                    label.append(str(testTime.hour)+'.00')
                    data.append(Tempquery[i].temp)

            #first
            else:
                listTempPerHour.append(Tempquery[i].temp)
            hour=testTime.hour
        calTime=(float(Notificationquery[number].countdownFeeder)/60)/60
        mod=(calTime%1)
        koy=calTime-mod
        lastMod = (mod*60)/100
        result = koy+lastMod
        showTime= "{:.02f}".format(result)
        listDay=listDay[::-1]
        
        params={"product_id":int(product_id),
                "listFarm":listFarm,
                "user":user,
                "type":"farm",
                "content":Farmquery[number],
                "ListNameFarm":Farmquery,
                "Notification":Notificationquery[number],
                # "temp":temp,
                "listDay":listDay,
                "chartFarm":chartFarm,
                "showTime":showTime,
                'label':label,
                'data':data}
        self.response.write(chart.render(params))

class Register(webapp2.RequestHandler):
    def get(self):
        message=self.request.get('message')
        if(message=="erroruser"):
            header="มีผู้ใช้นี้อยู่ในระบบแล้ว"
        elif(message=="repassword"):
            header="รหัสผ่านไม่ตรงกัน"
        elif(message=="sameemail"):
            header="อีเมลล์ถูกใช้งานแล้ว"
        elif(message=="success"):
            header="สมัครสมาชิกสำเร็จ"
        elif(message=="loginfailed"):
            header="เข้าสู่ระบบไม่สำเร็จ"
        elif(message=="samefarm"):
            header="id farm ซ้ำ"
        elif(message=="farmsuccess"):
            header="สร้างฟาร์มสำเร็จ"
        elif(message=="updatefarm"):
            header="ตั้งค่าฟาร์มสำเร็จ"
        elif(message=="NoChart"):
            header="ยังไม่มีข้อมูล"
        elif(message=="nowchangewatererror"):
            header="เปลี่ยนน้ำตอนนี้ไม่สำเร็จ"
        elif(message=="nowchangewatersuccess"):
            header="เปลี่ยนน้ำตอนนี้สำเร็จ"
        elif(message=="nowfeedererror"):
            header="ให้อาหารตอนนี้ไม่สำเร็จ"
        elif(message=="nowfeedersuccess"):
            header="ให้อาหารตอนนี้สำเร็จ"
        elif(message=="errorDB"):
            header="มีปัญหาเกี่ยวกับฐานข้อมูลกรุณาติดต่อเจ้าหน้าที่"
        elif(message=="newpasswordsuccess"):
            header="เปลี่ยนรหัสผ่านเรียบร้อย"
        elif(message=="nousername"):
            header="ไม่มี user นี้อยู่ในระบบ"
        elif(message=="errornewpassword"):
            header="เปลี่ยนรหัสผ่านไมสมบูรณ์"
        elif(message=="haveNameFarm"):
            header="มีชื่อฟาร์มนี้อยู่ในระบบแล้ว"
        elif(message=="noSearch"):
            header="ไม่พบข้อมูลในระบบ"
        elif(message=="deletefarmerror"):
            header="ลบฟาร์มเลี้ยงไม่สำเร็จ"
        elif(message=="deletefarmsuccess"):
            header="ลบฟาร์มเลี้ยงสำเร็จ"
        else:
            header=message
        params={"header":header}
        self.response.write(regiserror.render(params))

class RegisUser(BaseHandler):
    def post(self):
        data = self.request
        username=data.get('username')
        password=data.get('password')
        repassword=data.get('repassword')
        phone=data.get('phone')
        email=data.get('email')
        unique_properties = ['email_address']
        if password !=repassword:
          self.redirect('/register?message=repassword')
          return
        user_data = self.user_model.create_user(username,
        unique_properties,email_address=email, 
        password_raw=password,phone=phone)
        self.response.out.write(str(user_data)) 
        error=user_data[1]
        if not user_data[0]:
            for i in error:
                if i=="auth_id":
                    self.redirect('/register?message=erroruser')
                    return
                if i == "email_address":
                    self.redirect('/register?message=sameemail')
                    return
        
        user = user_data[1]
        user_id = user.get_id()
        token = self.user_model.create_signup_token(user_id)
        self.redirect('/register?message=success')


class Repassword(BaseHandler):
    @user_required
    def get(self):
        user = self.user_info
        params={'user':user,
                'type':'repassword'}
        self.response.write(repassword.render(params))
        return
    def post(self):
        old_token = self.request.get('oldpassword')
        password = self.request.get('newpassword')
        if not password or password != self.request.get('renewpassword'):
          self.redirect('/register?message=errornewpassword')
          return
        user = self.user
        user.set_password(password)
        user.put()
        self.user_model.delete_signup_token(user.get_id(), old_token)
        self.redirect('/register?message=newpasswordsuccess')

class Resetpassword(BaseHandler):
    @user_required
    def get(self):
        user = self.user_info
        params={'user':user,
                'type':'repassword'}
        self.response.write(adminrepassword.render(params))
        return
    def post(self):
        user = self.request.get('id')
        old_token = self.request.get('oldpassword')
        password = self.request.get('newpassword')
        username = self.user_model.get_by_auth_id(user)
        if not username:
            self.redirect('/register?message=nousername')
        if not password or password != self.request.get('renewpassword'):
          self.redirect('/register?message=errornewpassword')
          return
        user_id = username.get_id()
        token = self.user_model.create_signup_token(user_id)
        username.set_password(password)
        username.put()
        self.redirect('/register?message=newpasswordsuccess')
        return
        
        # if not password or password != self.request.get('renewpassword'):
        #   self.redirect('/register?message=errornewpassword')
        #   return
        # user = self.user
        # user.set_password(password)
        # user.put()
        # self.user_model.delete_signup_token(user.get_id(), old_token)
        # self.redirect('/register?message=newpasswordsuccess')


class Login(BaseHandler):
    def get(sedlf):
        self._serve_page()
    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        try:
          u = self.auth.get_user_by_password(username, password, remember=True,
            save_session=True)
          self.redirect(self.uri_for('index'))
        except (InvalidAuthIdError, InvalidPasswordError) as e:
          self._serve_page(True)
    def _serve_page(self, failed=False):
        self.redirect('/register?message=loginfailed')
    def get(self):

        self.response.headers['Content-Type'] = 'text/html'
        # params={}
        if self.user==None:
            self.response.write(login.render())
            return
        else:
            self.redirect('/')
            return


class Logout(BaseHandler):
    @user_required
    def get(self):
        self.auth.unset_session()
        self.redirect(self.uri_for('login'))

class Index(BaseHandler):
    @user_required
    def get(self):
        Farmquery=getFarm(self.user_info)
        Notificationquery=getNotification(self.user_info)
        allFarm=len(getAllFarm(self.user_info))

        lenFarm=allFarm/10
        if allFarm%10 ==0:
            listPage=range(1,lenFarm+1)
        else:
            listPage=range(1,lenFarm+2)
        if Farmquery=="errorDB":
            self.redirect('/register?message=errorDB')
            return
        if Notificationquery=="errorDB":
            self.redirect('/register?message=errorDB')
            return
        listFarm=[]
        # try:
            # Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0]).fetch()
            # Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0]).fetch(limit=2)
        # except Exception as e:
            # self.redirect('/register?message=errorDB')
            # return
        count=1
        for i in getAllFarm(self.user_info):
            listFarm.append(count)
            count+=1
        product_id=None
        user = self.user_info
        # self.response.write(Notificationquery)
        # return
        params={"product_id":product_id,
                "listFarm":listFarm,
                "user":user,
                "type":"index",
                "ListNameFarm":getAllFarm(self.user_info),
                "content":Farmquery,
                "notification":Notificationquery,
                'page':1,
                "listPage":listPage}
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(index.render(params))

class Page(BaseHandler):
    @user_required
    def get(self, *args, **kwargs):
        page= int(kwargs['page'])-1
        Farmquery=getFarm(self.user_info,start=(page*10))
        Notificationquery=getNotification(self.user_info,start=(page*10))
        lenFarm=len(getAllFarm(self.user_info))/10
        listPage=range(1,lenFarm+2)
        if Farmquery=="errorDB" or Farmquery==[]:
            self.redirect('/register?message=errorDB')
            return
        listFarm=[]
        # try:
            # Farmquery=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0]).fetch()
            # Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0]).fetch()
        # except Exception as e:
            # self.redirect('/register?message=errorDB')
            # return
        count=1
        for i in getAllFarm(self.user_info):
            listFarm.append(count)
            count+=1
        product_id=None
        user = self.user_info
        params={"product_id":product_id,
                "listFarm":listFarm,
                "user":user,
                "type":"page",
                "ListNameFarm":getAllFarm(self.user_info),
                "content":Farmquery,
                "notification":Notificationquery,
                'page':page+1,
                "listPage":listPage}
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(index.render(params))

class Search(BaseHandler):
    @user_required
    def get(self, *args, **kwargs):
        user = self.user_info
        nameSearch= kwargs['name']

        allfarm=Farmdb.query().order(Farmdb.id).filter(Farmdb.user==self.user_info['auth_ids'][0],Farmdb.nameFarm==nameSearch).fetch()
        if allfarm==[]:
            self.redirect('/register?message=noSearch')
            return
        for i in allfarm:
            idFarm=i.id
        Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0],Notificationdb.idFarm==idFarm).fetch()
        product_id=None
        params={"product_id":product_id,
                "user":user,
                "type":"search",
                "content":allfarm,
                "notification":Notificationquery,
                'page':1}
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(search.render(params))

class Handchecking(BaseHandler):
    def get(self):
        # a={'Secretkey': 'secretkey', 'Raspberrypi_Mac': '5cf9dd52e02a'}
        # a=self.request.get('Data')
        # data = ast.literal_eval(a)
        # for i in data:
        secret='secretkey'
        if secret != "secretkey":
            self.response.write("Don't have permission")
            return
        mac='5cf9dd52e02a'
        farm=Farmdb.query().filter(Farmdb.macPi==mac).fetch()
        # self.response.write(farm)
        # return
        listFarm=[]
        for i in farm:
            listFarm.append({'idFarm':i.id,"idArduino":i.idArduino,'timeWater':i.timeWater,"wide":i.wide,"temp":i.temp,"timeEatDay":i.timeEatDay,"numberCrayfish":i.numberCrayfish})
        change=Changedb().query().filter(Changedb.macPi==mac)
        getChange=change.get()
        getChange.change=False
        getChange.put()
        self.response.write(listFarm)
    def post(self):
        secret=self.request.get('Secretkey')
        if secret != "secretkey":
            self.response.write("Don't have permission")
            return
        mac=self.request.get('Raspberrypi_Mac')
        farm=Farmdb.query().filter(Farmdb.macPi==mac).fetch()
        listFarm=[]
        for i in farm:
            listFarm.append({'idFarm':i.id,"idArduino":i.idArduino,'timeWater':i.timeWater,"wide":i.wide,"temp":i.temp,"timeEatDay":i.timeEatDay,"numberCrayfish":i.numberCrayfish})
        change=Changedb().query().filter(Changedb.macPi==mac)
        getChange=change.get()
        getChange.change=False
        getChange.put()
        self.response.write(listFarm)
        
class Piconnect(BaseHandler):
    def get(self):
        getTime=datetime.now()+timedelta(hours=7)
        time = str(getTime.time()).split(':')
        dayTime = createId(str(getTime.date())+" "+time[0]+":"+time[1])
        if int(dayTime.tm_min)%10==0:
            self.response.write(0);
            return
        else:
            self.response.write(int(dayTime.tm_min));
            return
        # notification=Notificationdb.query().filter(Notificationdb.idFarm=="f20170406274760")
        # for z in notification:
        #     if z.nowFeeder:
        #         nowFeeder=True
        #     if z.nowChangeWater:
        #         nowChangeWater=True

        # self.response.write(notification)
        # return
        
    def post(self):
        a=self.request.get('Data')
        secret=self.request.get('secret')
        mac=self.request.get('Raspberrypi_Mac')
        if secret != "":
            self.response.write("Don't have permission")
            return
        data = ast.literal_eval(a)
        checkChange=False
        farm=[]
        for i in data:
            change=Changedb().query().filter(Changedb.macPi==mac).fetch()
            for y in change:
                if y.change:
                    checkChange=True
            notification=Notificationdb.query().filter(Notificationdb.idFarm==i['FarmID'])
            nowFeeder=False
            nowChangeWater=False
            for z in notification:
                if z.nowFeeder:
                    nowFeeder=True
                if z.nowChangeWater:
                    nowChangeWater=True
            if nowFeeder or nowChangeWater:
                farm.append({"nowFeeder":nowFeeder,"nowChangeWater":nowChangeWater,"idFarm":i['FarmID']})
            

            editNotification=notification.get()
            if i['status_changewatersystem']:
                editNotification.nowChangeWater=False
            if i['status_feedersystem']:
                editNotification.nowFeeder=False
            editNotification.countdownChangeWater=i['Countdown_change_water']
            editNotification.temperature=i['Temperature']
            editNotification.statusFeed=i['Status_feed']
            editNotification.countdownFeeder=i['Countdown_feeder']
            editNotification.statusChangewatersystem=i['status_changewatersystem']
            editNotification.statusFeedersystem=i['status_feedersystem']
            editNotification.statusCoolersystem=i['status_coolersystem']
            editNotification.time=datetime.now()
            editNotification.put()

            getTime=datetime.now()+timedelta(hours=7)
            time = str(getTime.time()).split(':')
            dayTime = createId(str(getTime.date())+" "+time[0]+":"+time[1])
            idFarm =i['FarmID']
            temp=i['Temperature']
            dateSave=datetime(dayTime.tm_year,dayTime.tm_mon,dayTime.tm_mday)
            tempDay=DayTempdb().query().filter(DayTempdb.idFarm==idFarm).fetch()
            check=False
            for i in tempDay:
                if i.day==dateSave:
                    check=True
                    break   
            if not check:
                saveDay=DayTempdb()
                saveDay.idFarm=idFarm
                saveDay.day=dateSave
                saveDay.put()
            if int(dayTime.tm_min)%10==0:
                tempsave=Tempdb()
                tempsave.idFarm=idFarm
                tempsave.temp=temp
                tempsave.day=dateSave
                tempsave.put()
            
        di={'change':checkChange,"listDonow":farm}
        self.response.write(di)
        return

class DeleteFarm(BaseHandler):
    def post(self, *args, **kwargs):
        try:
            idfarm= kwargs['idfarm']
            Farmquery=Farmdb.query(Farmdb.user==self.user_info['auth_ids'][0],Farmdb.id==idfarm)
            thisFarmquery = Farmquery.get()
            thisFarmquery.key.delete()

            Notiquery=Notificationdb.query(Notificationdb.user==self.user_info['auth_ids'][0],Notificationdb.idFarm==idfarm)
            thisNotiquery = Notiquery.get()
            thisNotiquery.key.delete()

            # thisFarmquery.nowFeeder=True
            # thisFarmquery.put()
        except Exception as e:
            self.redirect('/register?message=deletefarmerror')
            return
        self.redirect('/register?message=deletefarmsuccess')
        return    
        # self.redirect('/register?message=nowfeedersuccess')
        # return
class TestDb(BaseHandler):
    def get(self):
        # Farm = ndb.Key('Farmdb', 123)
        # self.response.write(Farm)
        # return
        # ndb.delete_multi(
        #     Tempdb.query().fetch(keys_only=True)
        # )
        # ndb.delete_multi(
        #     DayTempdb.query().fetch(keys_only=True)
        # )
        idFarm="f201704182143400"
        tempDay=DayTempdb().query().filter(DayTempdb.idFarm==idFarm).fetch()
        check=False
        getTime=datetime.now()+timedelta(hours=7)
        time = str(getTime.time()).split(':')
        dayTime = createId(str(getTime.date())+" "+time[0]+":"+time[1])
        dateSave=datetime(dayTime.tm_year,dayTime.tm_mon,dayTime.tm_mday)
        for i in tempDay:
            if i.day==dateSave:
                check=True
                break   
        if not check:
            saveDay=DayTempdb()
            saveDay.idFarm=idFarm
            saveDay.day=dateSave
            saveDay.put()
        
        tempsave=Tempdb()
        tempsave.idFarm="f201704182143400"
        tempsave.temp=27.1
        tempsave.day=dateSave
        tempsave.put()
        self.response.write('success')
        return

class FeedNow(BaseHandler):
    def post(self, *args, **kwargs):
        try:
            idfarm= kwargs['idfarm']
            Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0],Notificationdb.idFarm==idfarm)
            thisNotification = Notificationquery.get()
            thisNotification.nowFeeder=True
            thisNotification.put()
        except Exception as e:
            self.redirect('/register?message=nowfeedererror')
            return
        self.redirect('/register?message=nowfeedersuccess')

class WaterNow(BaseHandler):
    def post(self, *args, **kwargs):
        try:
            idfarm= kwargs['idfarm']
            Notificationquery=Notificationdb.query().order(Notificationdb.idFarm).filter(Notificationdb.user==self.user_info['auth_ids'][0],Notificationdb.idFarm==idfarm)
            thisNotification = Notificationquery.get()
            thisNotification.nowChangeWater=True
            thisNotification.put()
        except Exception as e:
            self.redirect('/register?message=nowchangewatererror')
            return
        self.redirect('/register?message=nowchangewatersuccess')

# a = db().filter().fetch()
# for i in a:
#   i.get()

config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ["auth_ids",'email_address']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'FUCKYOUNOOB',
    #ตั้ง session หมดอายุ วินาที
    'session_max_age': 6000
  }
}

app = webapp2.WSGIApplication([
    webapp2.Route('/', Index, name='index'),
    webapp2.Route('/page/<page:\d+>', Page, name='page'),
    webapp2.Route('/farm/<product_id:\d+>', Farm, name="farm"),
    webapp2.Route('/admin/reset/password', Resetpassword, name="resetpassword"),
    webapp2.Route('/deletefarm/<idfarm>', DeleteFarm, name="deleteFarm"),
    webapp2.Route('/testdb', TestDb, name="testdb"),
    webapp2.Route('/search/<name>', Search, name="search"),
    webapp2.Route('/farm/<idfarm>/feednow', FeedNow, name="FeedNow"),
    webapp2.Route('/farm/<idfarm>/waternow', WaterNow, name="WaterNow"),
    webapp2.Route('/login', Login, name='login'),
     webapp2.Route('/repassword',Repassword, name="repassword"),
    webapp2.Route('/logout', Logout, name='logout'),
    webapp2.Route('/regis', RegisUser, name="regisuser"),
    webapp2.Route('/register', Register, name="register"),
    webapp2.Route('/createfarm',Createfarm, name="createfarm"),
    webapp2.Route('/configfarm/<product_id:\d+>',Configfarm, name="configfarm"),
    # webapp2.Route('/chart/<product_id:\d+>',Chart, name="chart"),
    webapp2.Route('/chart/<product_id:\d+>/<day:\d+>/<month:\d+>/<year:\d+>',ChartDay, name="chartday"),
    webapp2.Route('/handchecking',Handchecking, name="handchecking"),
    webapp2.Route('/piconnect',Piconnect, name="piconnect"),
    webapp2.Route('/getnotification',Getnoti, name="getnoti"),
    # webapp2.Route('/.*',NotFoundPageHandler, name="notfound"),
], debug=True,config=config)
