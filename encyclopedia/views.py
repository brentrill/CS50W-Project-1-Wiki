from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from random import choice
from . import util
from markdown2 import Markdown

# Django Form Classes
class SearchForm(forms.Form):
    search = forms.CharField(label="Search Wiki")

class CreatePageForm(forms.Form):
    title = forms.CharField(label="Title",
    widget = forms.TextInput(attrs={'style': 'width: 65vw;'}))

    content = forms.CharField(required= False,
    widget = forms.Textarea(attrs={'placeholder':'Enter markdown content',
                                    'style': 'height: 16em;'}))

class EditPageForm(forms.Form):
    title = forms.CharField(label="Title", disabled=False, required = True,
    widget= forms.HiddenInput)
   
    content = forms.CharField(required= False,
    widget= forms.Textarea(attrs={'style': 'height: 16em'}))


form = SearchForm()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": form
    })

"""
Function entry() takes the title from the URL and
gets the related entry content, converting it form markdown to HTML.
If the entry exists, it will return the entry's wiki page. If not, 
it will return the error page.
"""
def entry(request, title):
    markdown_content = util.get_entry(title)
    markdowner = Markdown()

    if markdown_content:
        entry_html = markdowner.convert(markdown_content)
    else:
        return render(request, "encyclopedia/error.html" )   

    return render(request, "encyclopedia/entry.html", {
        "entry_html": entry_html,
        "title": title,
        "form": form
    })

"""
search function gets a query from Django form.
Then if the query exists as a page, it will return the entry
function with the query passed as the title.
If the query doesn't match an existing page, it will compile a list of
entries whose title has a matching substring.
"""
def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data["search"]

    if util.get_entry(query):
        return entry(request, query)
    else:
        results = [x for x in util.list_entries() if query.lower() in x.lower()]
        return render(request, "encyclopedia/search.html", {
            "results": results,
            "query": query,
            "form": form
        })

"""
The new_page function renders new.html containing a new Django form
receiving a title for a new entry and markdown content. If the new title
matches an existing entry, it will render the new page again with an error
message. If it passes that check, the new entry is saved to disk and the
user is redirected to the new page.
"""
def new_page(request):
    if request.method == "POST":
        new_form = CreatePageForm(request.POST)
        
        if new_form.is_valid():
            title = new_form.cleaned_data["title"]
            content = new_form.cleaned_data["content"]

            # Check for existing entry
            if util.get_entry(title):
                error = f"Error: Entry '{title}' already exists."
                return render(request, "encyclopedia/new.html", {
                    "form": form,
                    "new_form": CreatePageForm(),
                    "error": error
                })

            util.save_entry(title, content)
            return entry(request, title)

        else:
            return render(request, "encyclopedia/new.html", {
                "form": form,
                "new_form": new_form
            })
    
    return render(request, "encyclopedia/new.html", {
        "form": form,
        "new_form": CreatePageForm()
    })

"""
edit_page creates a Django form that fills the inputs with that entries
content, obtained from the title given by the submit button on the previous
page. The title field is hidden to prevent conflicts.
"""
def edit_page(request):
    title = request.POST.get("title")
    edit_form = EditPageForm(initial={'title': title, 'content': util.get_entry(title)})

    if edit_form.is_valid():
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "edit_form": edit_form,
            "title": title
        })

    else:
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "edit_form": edit_form,
            "title": title
        })

"""
change_page gets the new entry content from edit.html and then saves
it to the disk, redirecting to the updated entry.
"""
def change_page(request):
    edit_form = EditPageForm(request.POST)

    if edit_form.is_valid():
        title = edit_form.cleaned_data["title"]
        content = edit_form.cleaned_data["content"].encode()

        util.save_entry(title, content)
        return entry(request, title)
        
    else:
        return render(request, "encyclopedia/edit.html", {
            "form": form,
            "edit_form": edit_form,
            "title": title
        })

"""
random_page returns entry() with a random title from the 
list of all entries as the parameter.
"""
def random_page(request):
    return entry(request, choice(util.list_entries()))