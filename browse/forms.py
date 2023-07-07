# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render


@login_required
def change_password(request, template="browse/password_change_form.html"):
    form = PasswordChangeForm(user=request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            context = {"form": form, "success": True}
            return render(request, template, context)

    context = {"form": form}
    return render(request, template, context)
