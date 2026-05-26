import time
import logging

from django.shortcuts import render

from apps.knowledge.models import KnowledgeBase
from .services.retriever import retrieve
from .services.generator import generate

logger = logging.getLogger(__name__)


def ask(request):
    kb_list = KnowledgeBase.objects.all()
    context = {'kb_list': kb_list}

    if request.method == 'POST':
        kb_id = request.POST.get('kb_id', '')
        question = request.POST.get('question', '').strip()

        if not kb_id or not question:
            context['error'] = '请选择知识库并输入问题'
            return render(request, 'rag/ask.html', context)

        start = time.time()
        try:
            chunks = retrieve(kb_id=int(kb_id), query=question)
            elapsed_ms = int((time.time() - start) * 1000)

            if not chunks:
                context['answer'] = '当前知识库中未找到足够依据来回答这个问题。'
                context['citations'] = []
                context['trace_id'] = 'no-hits'
                context['elapsed_ms'] = elapsed_ms
                return render(request, 'rag/ask.html', context)

            result = generate(question, chunks)
            elapsed_ms = int((time.time() - start) * 1000)

            context['question'] = question
            context['answer'] = result.answer
            context['citations'] = result.citations
            context['trace_id'] = result.trace_id
            context['elapsed_ms'] = elapsed_ms

        except Exception as e:
            logger.exception('问答失败')
            context['error'] = str(e)

    return render(request, 'rag/ask.html', context)
