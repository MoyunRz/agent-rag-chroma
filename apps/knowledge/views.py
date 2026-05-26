from django.shortcuts import redirect, render

from apps.ingestion.models import Document
from .models import KnowledgeBase


def index(request):
    kb_list = KnowledgeBase.objects.all()
    docs = Document.objects.order_by('-created_at')[:20]
    return render(request, 'knowledge/index.html', {
        'kb_list': kb_list,
        'documents': docs,
    })


def create_kb(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        desc = request.POST.get('description', '').strip()
        if name:
            KnowledgeBase.objects.create(name=name, description=desc)
    return redirect('knowledge:index')
