from markdown import markdown
import random
from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util

class SearchForm(forms.Form):
    qentry = forms.CharField(label="", widget=forms.TextInput(attrs={'class':'search', 'placeholder':"Пошук статті"}))

class NewEntryForm(forms.Form):
    title = forms.CharField(label="Додайте заголовок статті", widget=forms.TextInput(attrs={'class':'form-control', 'required': True}))
    entry = forms.CharField(label="Додайте текст статті", widget=forms.Textarea(attrs={'class':'form-control', 'required': True}))


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if entry == None:
        entry = "**Такої статті не знайдено**"

    return render(request, "encyclopedia/entry.html", {
        "entry": markdown(str(entry)),
        "form": SearchForm(),
        "title": title
    })

def search(request):
    search_data = request.GET.dict()
    title = search_data.get("qentry")
    list_e = util.list_entries()
    print("title=", title, " list_e=", list_e)
    if title in list_e:
        return HttpResponseRedirect("wiki/"+title)

    entries = []
    for entry in list_e:
        if entry.lower().find(title.lower()) >= 0:
            entries.append(entry)

    if len(entries) == 1 :
        return HttpResponseRedirect("wiki/"+entries[0])  
    else:
        return render(request, "encyclopedia/search.html", {
            "entries" : entries,
            "form": SearchForm()
    })

def random_entry(request):
    list_e = util.list_entries()
    title = random.choice(list_e)
    return HttpResponseRedirect("wiki/"+title)

def add(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]
            if util.get_entry(title) == None:
                util.save_entry(title, entry)
                return HttpResponseRedirect("wiki/"+title)
            else:
               form.fields['title'].label = "Така стаття вже існує. Введіть іншу назву:"
               return render(request, "encyclopedia/add.html", {
                    "form": SearchForm(),
                    "neform": form
                })
        else: 
            return render(request, "encyclopedia/add.html", {
                "form": SearchForm(),
                "neform": form
            })

    return render(request, "encyclopedia/add.html", {
        "form": SearchForm(),
        "neform": NewEntryForm()
    })

def edit(request, title):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry = form.cleaned_data["entry"]
            util.save_entry(title, entry)
            return HttpResponseRedirect(reverse("encyclopedia:index")+"wiki/"+title)
    entry = util.get_entry(title)
    if entry == None:
        form = NewEntryForm()
        form.fields['title'].widget = forms.HiddenInput()
        form.fields['entry'].label = "Такої статті не знайдено. Ви можете її створити"
    else:
        form = NewEntryForm( {'title': title, 'entry': entry})
        form.fields['title'].widget = forms.HiddenInput()
        form.fields['entry'].label = "Змініть текст статті"

    return render(request, "encyclopedia/edit.html", {
        "form": SearchForm(),
        "neform": form,
        "title": title
    })






