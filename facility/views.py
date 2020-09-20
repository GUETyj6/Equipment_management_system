from django.shortcuts import render,redirect,get_object_or_404
from .models import Facility, Maintain,Repair,Scrap
from .forms import BaoxiuForm,FacilityForm, FacilitySelectForm, MaintainAppendForm, MaintainSelectForm, RepairedSelectForm,ScarpForm
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
import time

from django.shortcuts import HttpResponse
import xlwt
from io import StringIO,BytesIO#pyhton3
import datetime

def facility_document(request):
    facilities = Facility.objects.all()
    context= {}
    context['facilities'] = facilities
    return render(request, 'facility_document.html', context)


def maintain_document(request):
    facilities = Maintain.objects.all()
    context= {}
    context['facilities'] = facilities
    return render(request, 'maintain_document.html', context)


def baoxiu(request,user_pk):
    ur =get_object_or_404(User, pk=user_pk)
    if request.method == 'POST':
        baoxiu_form = BaoxiuForm(request.POST)
        if baoxiu_form.is_valid():
            question = baoxiu_form.cleaned_data['question']
            facility = baoxiu_form.cleaned_data['facility']
            faci_tem = Facility.objects.filter(facility_name=facility)[0]
            user_tel = ur.get_staff_tel()
            add = Repair(facility_id=faci_tem, baoxiu_staff_name=ur, baoxiu_staff_tel=user_tel, baoxiu_complementary=question )
            add.save()
            return redirect(reverse('baoxiu_list'))
            # send_mail('Subject here', '有一个故障需要您取处理.', '302857039@qq.com',
            #           ['302857039@qq.com'], fail_silently=False)
    else:
        baoxiu_form  = BaoxiuForm()
    context = {}
    context['baoxiu_form'] = baoxiu_form
    return render(request, 'baoxiu.html', context)


def baoxiu_list(request):
    repairs = Repair.objects.filter(repair_staff_name=None)
    context= {}
    context['repairs'] = repairs
    return render(request, 'baoxiu_list.html', context)

def dai_repair(request):
    repairs = Repair.objects.filter(repair_staff_name=None)
    context = {}
    context['count'] = repairs.count()
    context['repairs'] = repairs
    return render(request, 'dai_repair.html', context)

def repaired_list(request):
    repairs = Repair.objects.filter(~Q(repair_staff_name=None))
    context = {}
    context['count'] = repairs.count()
    context['repairs'] = repairs
    return render(request, 'repaired_list.html', context)

def mark_done(request,repair_pk,user_pk):
    user = request.user
    if user.is_authenticated:
        ur =get_object_or_404(User, pk=user_pk)
        repair_tem = Repair.objects.get(pk=repair_pk)
        repair_tem.repair_staff_name = ur
        repair_tem.save()
        return redirect(reverse('dai_repair'))
    else:
        return redirect(reverse('login'))


def facility_append(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            FacilityForms = FacilityForm(request.POST)
            if FacilityForms.is_valid():
                facility_name = FacilityForms.cleaned_data['facility_name']
                version = FacilityForms.cleaned_data['version']
                price = FacilityForms.cleaned_data['price']
                add = Facility(facility_name=facility_name, version=version,
                                   price=price, buyer=usr)
                add.save()
                return redirect(reverse('facility_document'))
        else:
            FacilityForms = FacilityForm()
            context = {}
            context['FacilityForms'] = FacilityForms
            return render(request, 'facility_append.html', context)
    else:
        return redirect(reverse('login'))


def facility_select(request):

    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            FacilitySelectForms = FacilitySelectForm(request.POST)
            if FacilitySelectForms.is_valid():
                keyword = FacilitySelectForms.cleaned_data['keyword']
                valueword = FacilitySelectForms.cleaned_data['valueword']
                ans_tem = []
                print(keyword, valueword)
                if keyword == '1':#设备名称
                    ans_tem = Facility.objects.filter(Q(facility_name__contains=valueword))

                if keyword == '2':#购买时间
                    ans_tem = Facility.objects.filter(buy_time__contains=valueword)
                if keyword == '3':#购买人
                    ans_tem1 = User.objects.filter(Q(username__contains=valueword))
                    ans_tem = Facility.objects.filter(buyer__in=ans_tem1)

                if keyword == '4':#购买价格
                    ans_tem = Facility.objects.filter(price=valueword)

                context = {}
                context['facilities'] = ans_tem
                return render(request, 'facility_document.html', context)
        else:
            FacilitySelectForms = FacilitySelectForm()
            context = {}
            context['FacilitySelectForms'] = FacilitySelectForms
            return render(request, 'facility_select.html', context)
    else:
        return redirect(reverse('login'))


def facility_modify(request, facility_pk):
    usr = request.user
    if usr.is_authenticated:
        facility_tem = Facility.objects.get(pk=facility_pk)
        if request.method == 'POST':
            FacilityForms = FacilityForm(request.POST)
            if FacilityForms.is_valid():
                facility_tem.facility_name = FacilityForms.cleaned_data['facility_name']
                facility_tem.version = FacilityForms.cleaned_data['version']
                facility_tem.price = FacilityForms.cleaned_data['price']
                facility_tem.save()
                return redirect(reverse('facility_document'))
        else:
            FacilityForms = FacilityForm(initial={'facility_name':facility_tem.facility_name, 'version':facility_tem.version,'price':facility_tem.price})
            context = {}
            context['FacilityForms'] = FacilityForms
            return render(request, 'facility_modify.html', context)
    else:
        return redirect(reverse('login'))


def facility_delete(request, facility_pk):
    usr = request.user
    if usr.is_authenticated:
        pos = Facility.objects.get(pk=facility_pk)
        pos.delete()
        return redirect(reverse('facility_document'))
    else:
        return redirect(reverse('login'))


def maintain_append(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            MaintainAppendForms = MaintainAppendForm(request.POST)
            if MaintainAppendForms.is_valid():

                facility_tem= Facility.objects.get(facility_name=MaintainAppendForms.cleaned_data['facility_id'])
                complmentary = MaintainAppendForms.cleaned_data['complmentary']

                add = Maintain(facility_id=facility_tem, complmentary=complmentary,
                                   staff_name=usr)
                add.save()
                return redirect(reverse('maintain_document'))
        else:
            MaintainAppendForms = MaintainAppendForm()
            context = {}
            context['MaintainAppendForms'] = MaintainAppendForms
            return render(request, 'maintain_append.html', context)
    else:
        return redirect(reverse('login'))


def maintain_modify(request, maintain_pk):
    usr = request.user
    if usr.is_authenticated:
        maintain_tem = Maintain.objects.get(pk=maintain_pk)
        if request.method == 'POST':
            MaintainAppendForms = MaintainAppendForm(request.POST)
            if MaintainAppendForms.is_valid():
                maintain_tem.facility_id = Facility.objects.get(facility_name=MaintainAppendForms.cleaned_data['facility_id'])
                maintain_tem.complmentary = MaintainAppendForms.cleaned_data['complmentary']

                maintain_tem.save()
                return redirect(reverse('maintain_document'))
        else:
            MaintainAppendForms = MaintainAppendForm(initial={'facility_id':maintain_tem.facility_id, 'complmentary':maintain_tem.complmentary})
            context = {}
            context['MaintainAppendForms'] = MaintainAppendForms
            return render(request, 'maintain_modify.html', context)
    else:
        return redirect(reverse('login'))


def maintain_select(request):

    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            MaintainSelectForms = MaintainSelectForm(request.POST)
            if MaintainSelectForms.is_valid():
                keyword = MaintainSelectForms.cleaned_data['keyword']
                valueword = MaintainSelectForms.cleaned_data['valueword']
                ans_tem = []
                print(keyword, valueword)
                if keyword == '1':#设备名称
                    ans_tem1 = Facility.objects.filter(Q(facility_name__contains=valueword))
                    ans_tem = Maintain.objects.filter(facility_id__in=ans_tem1)

                if keyword == '2':#购买人
                    ans_tem1 = User.objects.filter(Q(username__contains=valueword))
                    ans_tem = Maintain.objects.filter(staff_name__in=ans_tem1)


                context = {}
                context['facilities'] = ans_tem
                return render(request, 'maintain_document.html', context)
        else:
            MaintainSelectForms = MaintainSelectForm()
            context = {}
            context['MaintainSelectForms'] = MaintainSelectForms
            return render(request, 'maintain_select.html', context)
    else:
        return redirect(reverse('login'))


def repaired_select(request):

    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            RepairedSelectForms = RepairedSelectForm(request.POST)
            if RepairedSelectForms.is_valid():
                keyword = RepairedSelectForms.cleaned_data['keyword']
                valueword = RepairedSelectForms.cleaned_data['valueword']
                ans_tem = []
                if keyword == '1':#设备名称
                    ans_tem1 = Facility.objects.filter(Q(facility_name__contains=valueword))
                    ans_tem = Repair.objects.filter(facility_id__in=ans_tem1)

                if keyword == '2':#报修人
                    ans_tem1 = User.objects.filter(Q(username__contains=valueword))
                    ans_tem = Repair.objects.filter(Q(baoxiu_staff_name__in=ans_tem1),~Q(repair_staff_name=None))
                if keyword == '3':#维修人
                    ans_tem1 = User.objects.filter(Q(username__contains=valueword))
                    ans_tem = Repair.objects.filter(repair_staff_name__in=ans_tem1)


                context = {}
                print(ans_tem.count())
                context['count'] = ans_tem.count()
                context['repairs'] = ans_tem
                return render(request, 'repaired_list.html', context)
        else:
            RepairedSelectForms = RepairedSelectForm()
            context = {}
            context['MaintainSelectForms'] = RepairedSelectForms
            return render(request, 'maintain_select.html', context)
    else:
        return redirect(reverse('login'))


def maintain_delete(request, maintain_pk):
    usr = request.user
    if usr.is_authenticated:
        pos = Maintain.objects.get(pk=maintain_pk)
        pos.delete()
        return redirect(reverse('maintain_document'))
    else:
        return redirect(reverse('login'))


def scrap(request):  #报废列表
    scraps = Scrap.objects.filter()
    context = {}
    context['scraps'] = scraps
    return render(request, 'scrap.html', context)

def add_scrap(request,user_pk): #申请报废
    usr = request.user
    ur = get_object_or_404(User,pk=user_pk)
    if request.method == 'POST':
        baofei_form = ScarpForm(request.POST)
        if baofei_form.is_valid():
            facility_tem = Facility.objects.get(facility_name=baofei_form.cleaned_data['facility_id'])
            question = baofei_form.cleaned_data['question']
            facility = baofei_form.cleaned_data['facility_id']
            add = Scrap(facility_id = facility_tem,baofei_staff_name =ur,baofei_complementary=question,scarp_time=time.time())
            add.save()
    else:
        baofei_form = ScarpForm()
    context = {}
    context['baofei_form'] = baofei_form
    return render(request, 'baofei.html', context)

def facility_download(request):
    usr = request.user
    if usr.is_authenticated:
        facilities = Facility.objects.all()
        context = {}
        context['facilities'] = facilities

        response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        response['Content-Disposition'] = 'attachment;filename='+str(now_time)+"-facilities.xls"  # 指定返回文件名
        wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
        sheet = wb.add_sheet(u'类别')  # excel里添加类别
        sheet.write(0, 0, '名称')
        sheet.write(0, 1, '型号')
        sheet.write(0, 2, '价格')
        sheet.write(0, 3, '购买人')
        sheet.write(0, 4, '购买时间')
        row = 1
        for facility in facilities:
            sheet.write(row, 0, str(facility.facility_name))
            sheet.write(row, 1, str(facility.version))
            sheet.write(row, 2, str(facility.price))
            sheet.write(row, 3, str(facility.buyer))
            sheet.write(row, 4, str(facility.buy_time))
            row = row + 1
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

        # return render(request, 'order_list.html', context)
    else:
        return redirect(reverse('login'))


def maintain_download(request):
    usr = request.user
    if usr.is_authenticated:
        facilities = Maintain.objects.all()
        context = {}
        context['facilities'] = facilities

        response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        response['Content-Disposition'] = 'attachment;filename='+str(now_time)+"-maintain.xls"  # 指定返回文件名
        wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
        sheet = wb.add_sheet(u'类别')  # excel里添加类别
        sheet.write(0, 0, '设备')
        sheet.write(0, 1, '保养时间')
        sheet.write(0, 2, '负责员工')
        sheet.write(0, 3, '补充')
        row = 1
        for facility in facilities:
            sheet.write(row, 0, str(facility.facility_id))
            sheet.write(row, 1, str(facility.last_time))
            sheet.write(row, 2, str(facility.staff_name))
            sheet.write(row, 3, str(facility.complmentary))
            row = row + 1
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

        # return render(request, 'order_list.html', context)
    else:
        return redirect(reverse('login'))


def repaired_download(request):
    usr = request.user
    if usr.is_authenticated:
        repairs = Repair.objects.filter(~Q(repair_staff_name=None))
        context = {}
        context['count'] = repairs.count()
        context['repairs'] = repairs

        response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        response['Content-Disposition'] = 'attachment;filename='+str(now_time)+"-repair.xls"  # 指定返回文件名
        wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
        sheet = wb.add_sheet(u'类别')  # excel里添加类别
        sheet.write(0, 0, '故障设备')
        sheet.write(0, 1, '报修人')
        sheet.write(0, 2, '联系方式')
        sheet.write(0, 3, '故障描述')
        sheet.write(0, 4, '报修时间')
        sheet.write(0, 5, '报修人')
        sheet.write(0, 6, '维修时间')
        row = 1
        for repair in repairs:
            sheet.write(row, 0, str(repair.facility_id))
            sheet.write(row, 1, str(repair.baoxiu_staff_name))
            sheet.write(row, 2, str(repair.baoxiu_staff_tel))
            sheet.write(row, 3, str(repair.baoxiu_complementary))
            sheet.write(row, 4, str(repair.baoxiu_time))
            sheet.write(row, 5, str(repair.repair_staff_name))
            sheet.write(row, 6, str(repair.repair_time))
            row = row + 1
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

    else:
        return redirect(reverse('login'))




def scarp_download(request):
    usr = request.user
    if usr.is_authenticated:
        repairs = Repair.objects.filter(~Q(repair_staff_name=None))
        scraps = Scrap.objects.filter()
        context = {}
        context['scraps'] = scraps

        response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        response['Content-Disposition'] = 'attachment;filename='+str(now_time)+"-scrap.xls"  # 指定返回文件名
        wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
        sheet = wb.add_sheet(u'类别')  # excel里添加类别
        sheet.write(0, 0, '报废设备')
        sheet.write(0, 1, '故障描述')
        sheet.write(0, 2, '报废时间')
        sheet.write(0, 3, '上报人员')

        row = 1
        for scrap in scraps:
            sheet.write(row, 0, str(scrap.facility_id))
            sheet.write(row, 1, str(scrap.baofei_complementary))
            sheet.write(row, 2, str(scrap.scarp_time))
            sheet.write(row, 3, str(scrap.baofei_staff_name))
            row = row + 1
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

    else:
        return redirect(reverse('login'))