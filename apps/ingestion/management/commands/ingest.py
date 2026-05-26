"""python manage.py ingest --kb-id 1 --file /path/to/doc.pdf"""
import argparse

from django.core.management.base import BaseCommand

from apps.ingestion.pipeline import ingest_document


class Command(BaseCommand):
    help = '入库单个文档到知识库'

    def add_arguments(self, parser):
        parser.add_argument('--kb-id', type=int, required=True)
        parser.add_argument('--file', type=str, required=True)
        parser.add_argument('--tenant', type=str, default='demo')

    def handle(self, *args, **options):
        doc = ingest_document(
            kb_id=options['kb_id'],
            file_path=options['file'],
            tenant_id=options['tenant'],
        )
        self.stdout.write(self.style.SUCCESS(f'入库完成: {doc.title}'))
