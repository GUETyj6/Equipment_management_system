from django.shortcuts import render
from .models import Orders
from .forms import OrderForm, OrderSelectForm
from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from warehouse.models import Product
from django.core.mail import send_mail

from django.shortcuts import HttpResponse
import xlwt
from io import StringIO,BytesIO#pyhton3
import datetime

def order_list(request):
    order_lists = Orders.objects.all()
    context = {}
    context['order_lists'] = order_lists
    return render(request, 'order_list.html', context)


def order_modify(request, order_pk):
    usr = request.user
    if usr.is_authenticated:
        order_tem = Orders.objects.get(pk=order_pk)
        if request.method == 'POST':
            ordermodifyform = OrderForm(request.POST)
            if ordermodifyform.is_valid():
                print(ordermodifyform.cleaned_data['order_name'])
                order_tem.order_name = Product.objects.get(product_name=ordermodifyform.cleaned_data['order_name'])
                order_tem.order_client = ordermodifyform.cleaned_data['order_client']
                order_tem.order_number = ordermodifyform.cleaned_data['order_number']
                order_tem.order_price = ordermodifyform.cleaned_data['order_price']
                order_tem.order_total_price = ordermodifyform.cleaned_data['order_total_price']
                order_tem.order_end = ordermodifyform.cleaned_data['order_end']
                order_tem.order_supplement = ordermodifyform.cleaned_data['order_supplement']
                order_tem.save()
                return redirect(reverse('order_list'))
        else:
            ordermodifyform = OrderForm(initial={'order_name':order_tem.order_name, 'order_client':order_tem.order_client,
                                                 'order_number':order_tem.order_number, 'order_price':order_tem.order_price,
                                                 'order_total_price':order_tem.order_total_price,'order_end':order_tem.order_end,
                                                 'order_supplement':order_tem.order_supplement})
            context = {}
            context['ordermodifyform'] = ordermodifyform
            return render(request, 'order_modify.html', context)
    else:
        return redirect(reverse('login'))


def order_delete(request, order_pk):
    usr = request.user
    if usr.is_authenticated:
        order_tem = Orders.objects.get(pk=order_pk)
        order_tem.delete()
        return redirect(reverse('order_list'))
    else:
        return redirect(reverse('login'))

def order_append(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            orderappendform = OrderForm(request.POST)
            if orderappendform.is_valid():
                order_name = orderappendform.cleaned_data['order_name']
                order_tem = Product.objects.get(product_name=order_name)
                order_client = orderappendform.cleaned_data['order_client']
                order_number = orderappendform.cleaned_data['order_number']
                order_price = orderappendform.cleaned_data['order_price']
                order_total_price = orderappendform.cleaned_data['order_total_price']
                order_end = orderappendform.cleaned_data['order_end']
                order_supplement = orderappendform.cleaned_data['order_supplement']
                add = Orders(order_name=order_tem, order_client=order_client, order_number=order_number,order_price=order_price,
                             order_total_price=order_total_price, order_end=order_end, order_supplement=order_supplement)
                add.save()
                send_mail('Subject here', '有一个新的订单.', 'liujinhao0519@163.com',
                          ['liujinhao@secrul.cn'], fail_silently=False)
                return redirect(reverse('order_list'))
        else:
            orderappendform = OrderForm()
            context = {}
            context['orderappendform'] = orderappendform
            return render(request, 'order_append.html', context)
    else:
        return redirect(reverse('login'))


def order_select(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            OrderSelectForms = OrderSelectForm(request.POST)
            if OrderSelectForms.is_valid():
                keyword = OrderSelectForms.cleaned_data['keyword']
                valueword = OrderSelectForms.cleaned_data['valueword']
                ans_tem = []
                print(keyword, valueword)
                if keyword == '1':  # 产品
                    ans_tem1 = Product.objects.filter(product_name__contains=valueword)
                    ans_tem = Orders.objects.filter(order_name__in=ans_tem1)

                if keyword == '2':  # 客户
                    ans_tem = Orders.objects.filter(order_client__contains=valueword)

                context = {}
                context['order_lists'] = ans_tem
                return render(request, 'order_list.html', context)
        else:
            OrderSelectForms = OrderSelectForm()
            context = {}
            context['OrderSelectForms'] = OrderSelectForms
            return render(request, 'order_select.html', context)
    else:
        return redirect(reverse('login'))

def order_download(request):
    usr = request.user
    if usr.is_authenticated:
        order_lists = Orders.objects.all()
        context = {}
        context['order_lists'] = order_lists
        # for order in order_lists:
        #     print(type(order.id),order.id)
        #     print(type(order.order_name),str(order.order_name))
        #     < td > {{order.order_client}} < / td >
        #     < td > {{order.order_number}} < / td >
        #     < td > {{order.order_price}} < / td >
        #     < td > {{order.order_total_price}} < / td >
        # < td > {{order.order_time}} < / td >
        # < td > {{order.order_end}} < / td >
        # < td > {{order.order_supplement}} < / td >
        # print(order_lists)

        response = HttpResponse(content_type='application/vnd.ms-excel')  # 指定返回为excel文件
        now_time = datetime.datetime.now().strftime('%Y-%m-%d')
        response['Content-Disposition'] = 'attachment;filename='+str(now_time)+"-order.xls"  # 指定返回文件名
        wb = xlwt.Workbook(encoding='utf-8')  # 设定编码类型为utf8
        sheet = wb.add_sheet(u'类别')  # excel里添加类别
        sheet.write(0, 0, '订单号')
        sheet.write(0, 1, '产品名称')
        sheet.write(0, 2, '客户')
        sheet.write(0, 3, '数量')
        sheet.write(0, 4, '单价(元)')
        sheet.write(0, 5, '总价(元)')
        sheet.write(0, 6, '订货时间')
        sheet.write(0, 7, '交货时间')
        row = 1
        for order in order_lists:
            sheet.write(row, 0, str(order.id))
            sheet.write(row, 1, str(order.order_name))
            sheet.write(row, 2, str(order.order_client))
            sheet.write(row, 3, str(order.order_number))
            sheet.write(row, 4, str(order.order_price))
            sheet.write(row, 5, str(order.order_total_price))
            sheet.write(row, 6, str(order.order_time))
            sheet.write(row, 7, str(order.order_supplement))
            row = row + 1
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response.write(output.getvalue())
        return response

        # return render(request, 'order_list.html', context)
    else:
        return redirect(reverse('login'))