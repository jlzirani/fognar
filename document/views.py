# Copyright 2012, Cercle Informatique. All rights reserved.

from config.json import json_send
from django.utils.html import escape
from document.models import Document, PendingDocument, Page
from document.forms import UploadHttpForm, UploadFileForm, RateDocumentForm
from django.contrib.contenttypes.models import ContentType
from djangbone.views import BackboneAPIView
from datetime import datetime
from re import match

from config.utils import get_context


class DocumentBone(BackboneAPIView):
    base_queryset = Document.objects.all()
    serialize_fields = ('id', 'name', 'description', 'uploader', "date",
                        'rating_average', 'rating_lower_bound', 'view_number',
                        'download_number')


class DocumentBoneTypeId(BackboneAPIView):
    base_queryset = Document.objects.all()
    serialize_fields = ('id', 'name', 'description', 'uploader', "date",
                        'rating_average', 'rating_lower_bound', 'rating_number',
                        'view_number', 'download_number')

    def dispatch(self, request, *args, **kwargs):
        thing = get_context(kwargs.get('type', None), kwargs.get('cid', None))
        c = ContentType.objects.get_for_model(thing)
        qs = DocumentBoneTypeId.base_queryset
        self.base_queryset = qs.filter(refer_oid=thing.id, refer_content=c)
        return super(DocumentBoneTypeId, self).dispatch(request,*args, **kwargs)


class PageBone(BackboneAPIView):
    base_queryset = Page.objects.all()
    serialize_fields = ('id', 'num', 'height_120', 'height_600', 'height_900')

    def dispatch(self, request, *args, **kwargs):
        try:
            doc = Document.objects.get(id=kwargs['did'])
            self.base_queryset = PageBone.base_queryset.filter(doc=doc)
        except:
            self.base_queryset = DocumentBone.base_queryset.none();
        return super(PageBone, self).dispatch(request,*args, **kwargs)


@json_send
def upload_file(request):
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid() and match(r'.*\.[pP][dD][fF]$',
                                 request.FILES['xfile'].name):
        data = form.cleaned_data
        thing = get_context(data['ctype'], data['context'])
        doc = Document.objects.create(name=escape(data['filename']),
                                      description=escape(data['description']),
                                      uploader=request.user.get_profile(),
                                      referer=thing,
                                      date=datetime.now())
        url = '/tmp/TMP402_%d.pdf' % doc.id
        tmp_doc = open(url, 'w')
        tmp_doc.write(request.FILES['xfile'].read())
        tmp_doc.close()
        PendingDocument.objects.create(doc=doc, state="queued", url='file://' + url)
        return '{"message": "ok"}'
    else:
        return '{"message": "invalid form"}'


@json_send
def upload_http(request):
    form = UploadHttpForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        thing = get_context(data['ctype'], data['context'])
        doc = Document.objects.create(name=escape(data['filename']),
                                      description=escape(data['description']),
                                      uploader=request.user.get_profile(),
                                      referer=thing,
                                      date=datetime.now())
        PendingDocument.objects.create(doc=doc, state="queued", url=data['url'])
        return '{"message": "ok"}'
    else:
        return '{"message": "invalid form"}'


@json_send
def rate(request):
    form = RateDocumentForm(request.POST)
    if form.is_valid():
        did = form.cleaned_data['did'];
        star = form.cleaned_data['star']
        if not (star > 0 and star < 6):
            return '{"message": "invalid vote"}'
        try:
            d = Document.objects.get(id=did);
        except:
            return '{"message": "invalid did"}'

        #TODO:
        #check first if the user already voted for that document, in that
        #case, remove his previous vote.

        setattr(d, 'rating_' + str(star), getattr(d, 'rating_' + str(star)) + 1)
        d.compute_rating()
        d.save()
        # check to see if MVC recommand to put this in a d.update_rating(params)
        # or something like that
        return '{"message": "rate succesful"}'
    else:
        return '{"message": "invalid form"}'
