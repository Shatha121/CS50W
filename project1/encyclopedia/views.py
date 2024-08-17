from django.shortcuts import render, redirect
import random
from . import util
from . import forms
from django.core.files import File
from django.contrib import messages
from django.urls import reverse

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def TITLE(request, title):
    content = util.get_entry(title)
    if content:
        return render(request, "encyclopedia/Entry.html", {
            "title": title,
            "content": util.convert_to_html(content)
        })
    else:
         return render(request, "encyclopedia/error.html", {
            "error": "Error message: there is no entry with this title",
        })

def search(request):
        search = request.GET.get('result')
        entry = util.get_entry(search)
        close_entry = []
        for i in util.list_entries() :
                        if search.lower() in i.lower():
                            close_entry.append(i)
        if entry:
            return render(request, "encyclopedia/Entry.html", {
                "title": entry
            })
        else:
             return render(request, "encyclopedia/Search.html", {
                    "close_entry": close_entry
            })
        

def create(request):
        if request.method == 'POST':
            
            newtitle = request.POST.get('add_title')
            content = request.POST.get('add_content')
            check_title = util.get_entry(newtitle)
            if newtitle == "" or content == "":
                return render(request, "encyclopedia/create.html", {
                    "Error": "Can't save with empty field."
                })
            if check_title:
                return render(request, "encyclopedia/create.html", {
                    "Error": "Error message: entry exists already"
                })
            else:
                util.save_entry(newtitle, content)
                return redirect("title", title=newtitle)
        else:
            return render(request, "encyclopedia/create.html")

        

def edit(request, title):
    entry = util.get_entry(title)
    if request.method == 'POST':
        content = request.POST.get('edit_content')
        if content.strip() == "":
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": content,
                "Error": "Can't save with empty field."
            })
        else:
            if entry:
                util.save_entry(title, content)
                return redirect("title", title=title)
            else:
                return render(request, "encyclopedia/edit.html", {
                    "Error": "The requested page was not found."
                })
    else:
        if entry:
            return render(request, "encyclopedia/edit.html", {
                "title": title,
                "content": entry
            })
        else:
            return render(request, "encyclopedia/edit.html", {
                "Error": "The requested page was not found."
            })

def random_entry(request):
    selected_title = random.choice(util.list_entries())
    selected_content = util.get_entry(selected_title)
    return render(request, "encyclopedia/Entry.html", {
        "title": selected_title,
        "content": selected_content
    })