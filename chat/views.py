from django.shortcuts import render, redirect
from django.views import View
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import models
from django.db.models import Q
# Create your views here.

class Main(View):
    def get(self, request):
        #request.session["get_me_from_the_consumer"] = "Hi this is me"
        #pass
        #print(request.session.get("get_me_from_the_main_page"))
        #data = {
        #    "type":"receiver_function",
        #    "message":"hi this is  event from view",
        # }
        #channel_layer = get_channel_layer()
        #async_to_sync(channel_layer.group_send)("test", data)
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return render(request=request, template_name="chat/main.html")
    
class Login(View):
    def get(self, request):
        #pass
        return render(request=request, template_name="chat/login.html")
    
    def post(self, request):

        context = {}
        data = request.POST.dict()

        username=data.get("username")
        password=data.get("password")
        try:
            user = authenticate(request=request, username=username, password=password)
            if user != None:
                login(request=request, user=user)
                #print("Usuario autenticado correctamente")
                return redirect("home")
                
            else:
                context.update({"error":"there is something wrong"})
               
            
        except Exception as e:
             context.update({"error":"the data is wrong"})

        return render(request=request, template_name="chat/login.html", context=context)
    
class Register(View):
    def get(self, request):
        #pass
        return render(request=request, template_name="chat/register.html")
    
    def post(self, request):

        context = {}
        data = request.POST.dict()
        #print(data)

        first_name=data.get("first_name")
        last_name=data.get("last_name")
        username=data.get("username")
        email=data.get("email")
        password=data.get("password")

        """ new_user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        ) """
        try:
            new_user = User()
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.username = username
            new_user.email = email
            new_user.set_password(password)
            new_user.save()
      
        
    
            user = authenticate(request=request, username=username, password=password)
            if user != None:
                login(request=request, user=user)
                #print("everything is fine and the data is right")
                return redirect("home")
                
            else:
                context.update({"error":"this mean that the data is wrong or there is something wrong"})
                #print("this mean that the data is wrong or there is something wrong")
        except Exception:
           
            context.update({"error":"the data is wrong"})

        return render(request=request, template_name="chat/register.html", context=context)
class Logout(View):
    def get(self, request):
        logout(request=request)
        return redirect("main")
        
class Home(View):
    def get(self, request):
        if request.user.is_authenticated:
            users = User.objects.all()
            context = {"user": request.user, "users": users}
            return render(request=request, template_name="chat/home.html", context=context)
        else:
            return redirect("main")
    
class ChatPerson(View):
    def get(self, request, id):
        
        """ if  request.user.is_authenticated:
            
            context = {"user": request.user}
            return render(request=request, template_name="chat/chat_person.html", context=context)
        else:
            return redirect("main")
         """
        if request.user.is_authenticated:
            person = User.objects.get(id=id)
            me = request.user
            messages = models.Message.objects.filter(
                Q(from_who = me , to_who = person) | Q(from_who = person , to_who = me)
                ).order_by("date","time") 
            
            
            user_channel_name = models.UserChannel.objects.get(user=person)
            data = {
                    "type":"receiver_function",
                    "type_of_data":"messages_seen",
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(user_channel_name.channel_name, data)

            messages_seen = models.Message.objects.filter(from_who=person, to_who=me)
            messages_seen.update(has_been_seen=True)

            context = {
                "person": person,
                "me": me
                ,"messages": messages
            }
            
            return render(request=request, template_name="chat/chat_person.html", context=context)
        else:
            return redirect("main")