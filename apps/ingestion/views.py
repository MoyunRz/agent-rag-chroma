import os

from django.conf import settings
from django.shortcuts import redirect, render

from apps.ingestion.pipeline import ingest_document
from apps.ingestion.models import Document, DocumentVersion
from apps.knowledge.models import KnowledgeBase


def index(request):
    kb_list = KnowledgeBase.objects.all()
    docs = Document.objects.order_by('-created_at')[:20]
    return render(request, 'ingestion/index.html', {
        'kb_list': kb_list,
        'documents': docs,
    })


def upload(request):
    if request.method != 'POST':
        return redirect('ingestion:index')

    kb_id = request.POST.get('kb_id')
    file = request.FILES.get('file')

    if not kb_id or not file:
        return render(request, 'ingestion/index.html', {
            'error': '请选择知识库并上传文件',
            'kb_list': KnowledgeBase.objects.all(),
        })

    # 保存到本地
    save_dir = os.path.join(settings.STORAGE_DIR, str(kb_id))
    os.makedirs(save_dir, exist_ok=True)
    file_path = os.path.join(save_dir, file.name)
    with open(file_path, 'wb') as f:
        for chunk in file.chunks():
            f.write(chunk)

    try:
        doc = ingest_document(kb_id=int(kb_id), file_path=file_path)
        msg = f'入库成功: {doc.title}'
        error = None
    except Exception as e:
        msg = None
        error = str(e)

    kb_list = KnowledgeBase.objects.all()
    docs = Document.objects.order_by('-created_at')[:20]
    return render(request, 'ingestion/index.html', {
        'msg': msg, 'error': error,
        'kb_list': kb_list, 'documents': docs,
    })
