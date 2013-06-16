
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def landing(requests):
    return redirect('cursivedata:index')
