from django.shortcuts import render, redirect,get_object_or_404  # para redireccionar
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm # para pedir un formulario
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate # import para generar cokie de sesion una vez validadp
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'home.html')
    
def signup(request):
    if request.method == 'GET':
         return render(request, 'signup.html',{
        'form':UserCreationForm
       })
    else:
        if request.POST['password1']== request.POST['password2']:
            # register user
           try:
                user=User.objects.create(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)   # aqui crea la sesion en el chrome para losdatos ingresados
                return redirect('tasks')
                #return HttpResponse('user create sucessfull')
           except IntegrityError:
               return render(request, 'signup.html',{
                    'form':UserCreationForm,
                    "error": 'Username already exists'
                     })
    return render(request, 'signup.html',{
                    'form':UserCreationForm,
                    "error": 'Passwordd do not mach'
                     })
            
           # print(request.POST),
           # print('Obteniendo datos')
@login_required
def tasks(request):
    tasks= Task.objects.filter(user=request.user,datecompleted__isnull=True)#datecompleted__isnull=False
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks= Task.objects.filter(user=request.user,datecompleted__isnull=False).order_by('-datecompleted')#datecompleted__isnull=False
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def create_task(request): # metodo insert en bd utilizo el mismo modelo de forms
    if request.method=='GET':
        return render(request, 'create_task.html',{
        'form':TaskForm
        })
    else:
        try:
            form=TaskForm(request.POST)
            new_task= form.save(commit=False)
            new_task.user= request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
           return render(request, 'create_task.html',{
            'form':TaskForm,
            'error':'Please provide valida data'
             })

@login_required
def task_detail(request, task_id):
    #print(task_id)
    if request.method == 'GET':
        task=get_object_or_404(Task, pk=task_id, user=request.user)  # trae la tarea en concreto id
        form= TaskForm(instance=task) # para actualizar la misma tare a que se llama por una instancia
        return render(request, 'task_detail.html', {
            'task': task, 'form':form    #se llama la tarea y un formulario si se desea actualizar
        } )
    else:
        try:
            task=get_object_or_404(Task,pk=task_id, user=request.user)
            form=TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            render(request, 'task_detail.html', {
            'task': task, 'form':form, 'error': "Error updating task"    #se llama la tarea y un formulario si se desea actualizar solo la del usuario
        } )
            
@login_required     
def complete_task(request, task_id):
     task=get_object_or_404(Task, pk=task_id, user=request.user) 
     if request.method== 'POST':
         task.datecompleted = timezone.now()
         task.save()
         return redirect('tasks')  
  
@login_required     
def delete_task(request, task_id):
     task=get_object_or_404(Task, pk=task_id, user=request.user) 
     if request.method== 'POST':
         task.delete()
         return redirect('tasks')  
      
@login_required        #decorador que restringe al que no esta logueado no permite ver 
def signout(request):   # cierra sesion cierra la cokie del navegador
    logout(request)
    return redirect('home')

def signin(request):
    if request.method =='GET':
        return render(request, 'signin.html',{
        'form':AuthenticationForm
        })
    else:
        #print (request.POST)
        user=authenticate(
            request, username=request.POST['username'], password=request.POST
            ['password'])
    if user is None:
                return render(request, 'signin.html',{
                     'form': AuthenticationForm,
                     'error':'Username or password is incorrect'
                })
    else:
        login(request, user)
        return redirect('tasks')
        
         
               
    
    
    

