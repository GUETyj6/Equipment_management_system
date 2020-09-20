from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, UserAppendForm, ChangePasswordForm, StaffTypeForm, UserModifyForm, AttendenceForm,\
    UserSelectForm, UserNormalSelectForm
from django.contrib import auth
from .models import Profile,Position
from django.db.models import Q
from user import waf
from django.contrib import messages
import time

def login(request):
    if request.method == 'POST':
        id = request.POST.get('username_or_email')
        passwd = request.POST.get('password')
        print(id,passwd)
        #检测是否是恶意请求
        flag,warning = waf.Predict(id+" "+passwd)
        print("id",id,"password",passwd)
        if flag:
            messages.warning(request, '请勿使用非法字符串')
            login_form = LoginForm()
            context = {}
            context['login_form'] = login_form
            return render(request, 'login.html',context)
        login_form = LoginForm(request.POST)
        print("login_form",login_form)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'login.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    context = {}
    return render(request, 'user_info.html', context)

def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)


def user_list(request):
    users = User.objects.all()
    context = {}
    context['users'] = users
    return render(request, 'user_list.html', context)





def apply(request):
    user = request.user
    if user.is_authenticated:
        if request.method == 'POST':
            apply_form = LoginForm(request.POST)
            if apply_form.is_valid():
                return redirect(request.GET.get('from', reverse('home')))
        else:
            apply_form = LoginForm()

        context = {}
        context['apply_form'] = apply_form
        return render(request, 'apply.html', context)
    else:
        return redirect(reverse('login'))


def user_delete(request, user_pk):
    #验证当前用户的登录状态
    user = request.user
    if user.is_authenticated:
        User.objects.get(pk=user_pk).delete()
        return redirect(reverse('user_list'))
    else:
        return redirect(reverse('login'))

def usermodify(request,user_pk):
    usr = request.user
    if usr.is_authenticated:
        user =get_object_or_404(User, pk=user_pk)
        if user.get_staff_gender() == '男':
            tem_gender = 'male'
        else:
            tem_gender = 'female'
        pro = Profile.objects.get(user=user)
        if request.method == 'POST':
            usermodify_form = UserModifyForm(request.POST)
            if usermodify_form.is_valid():
                user.username = usermodify_form.cleaned_data['username']
                pro.staff_type = usermodify_form.cleaned_data['type']
                pro.staff_gender = usermodify_form.cleaned_data['gender']
                pro.staff_age = usermodify_form.cleaned_data['age']
                pro.staff_home = usermodify_form.cleaned_data['home']
                pro.staff_nationality = usermodify_form.cleaned_data['nationality']
                pro.staff_tel = usermodify_form.cleaned_data['phone']
                pro.id_card = usermodify_form.cleaned_data['id_card']
                if usermodify_form.cleaned_data['password']:
                    user.set_password(usermodify_form.cleaned_data['password'])
                user.save()
                pro.save()
                return redirect(reverse('user_list'))

        usermodify_form = UserModifyForm(initial={'username':user.username, 'type':user.get_staff_type,
                                                   'gender':tem_gender,'age':user.get_staff_age,'home':user.get_staff_home,
                                                   'nationality':user.get_staff_nationality,'phone':user.get_staff_tel,
                                                   'id_card':user.get_id_card,'start_time':user.get_start_time,
                                                   })
        context = {}
        context['usermodify_form'] = usermodify_form
        return render(request, 'user_modify.html', context)
    else:
        return redirect(reverse('login'))


def userappend(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            usermodify_form = UserAppendForm(request.POST)
            if usermodify_form.is_valid():
                username = usermodify_form.cleaned_data['username']
                password = usermodify_form.cleaned_data['password']

                print(usermodify_form.cleaned_data['type'])
                if usermodify_form.cleaned_data['type'] == '经理':
                    add = User.objects.create_superuser(username,'', password)
                else:
                    add = User.objects.create_user(username, '',password)
                add.save()
                add.email = str(add.pk) + '@nbt.cn'
                add.save()
                staff_type = usermodify_form.cleaned_data['type']
                staff_gender = usermodify_form.cleaned_data['gender']
                staff_age = usermodify_form.cleaned_data['age']
                home = usermodify_form.cleaned_data['home']
                staff_nationality = usermodify_form.cleaned_data['nationality']
                staff_tel = usermodify_form.cleaned_data['phone']
                id_card = usermodify_form.cleaned_data['id_card']
                add1 = Profile(user=add, staff_type=staff_type, staff_gender=staff_gender, staff_age=staff_age, staff_home=home,
                               staff_nationality=staff_nationality, staff_tel=staff_tel, id_card=id_card,
                              )
                add1.save()
                return redirect(reverse('user_list'))
        usermodify_form = UserAppendForm()
        context = {}
        context['usermodify_form'] = usermodify_form
        return render(request, 'user_append.html', context)
    else:
        return redirect(reverse('login'))


def position_lists(request):
    position_lists = Position.objects.all()
    context = {}
    context['position_lists'] = position_lists
    return render(request, 'staff_type.html', context)


def staff_type_modify(request, position_pk):
    usr = request.user
    if usr.is_authenticated:
        pos = Position.objects.get(pk=position_pk)
        if request.method == 'POST':
            staff_modify_form = StaffTypeForm(request.POST)
            if staff_modify_form.is_valid():
                pos.position =staff_modify_form.cleaned_data['position']
                pos.save()
                return redirect(reverse('position_lists'))

        staff_modify_form = StaffTypeForm(initial={'position':pos.position})
        context = {}
        context['staff_modify_form'] = staff_modify_form
        return render(request, 'staff_type_modify.html', context)
    else:
        return redirect(reverse('login'))

def staff_type_delete(request, position_pk):
    usr = request.user
    if usr.is_authenticated:
        pos = Position.objects.get(pk=position_pk)
        pos.delete()
        return redirect(reverse('position_lists'))
    else:
        return redirect(reverse('login'))


def staff_type_add(request):
    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            staff_modify_form = StaffTypeForm(request.POST)
            if staff_modify_form.is_valid():

                pos=Position(position=staff_modify_form.cleaned_data['position'])
                pos.save()
                return redirect(reverse('position_lists'))
        else:
            staff_modify_form = StaffTypeForm
            context = {}
            context['staff_modify_form'] = staff_modify_form
            return render(request, 'staff_type_add.html', context)
    else:
        return redirect(reverse('login'))





def user_select(request):

    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            UserSelectForms = UserSelectForm(request.POST)
            if UserSelectForms.is_valid():
                keyword = UserSelectForms.cleaned_data['keyword']
                valueword = UserSelectForms.cleaned_data['valueword']
                pro_tem = []
                ans_tem = []
                print(keyword, valueword)
                if keyword == '1':#姓名
                    ans_tem = User.objects.filter(Q(username__contains=valueword))
                else:
                    if keyword == '2':#职位
                        pro_tem = Profile.objects.filter(staff_type__contains=valueword)
                    if keyword == '3':#性别
                        tem = 'male' if valueword == '男' else 'female'
                        pro_tem = Profile.objects.filter(staff_gender=tem)
                    if keyword == '4':#年龄
                        pro_tem = Profile.objects.filter(staff_age__contains=valueword)
                    if keyword == '5':#籍贯
                        pro_tem = Profile.objects.filter(staff_home__contains=valueword)
                    if keyword == '6':#民族
                        pro_tem = Profile.objects.filter(staff_nationality__contains=valueword)
                    if keyword == '7':#电话
                        pro_tem = Profile.objects.filter(staff_tel__contains=valueword)
                    if keyword == '8':#身份证
                        pro_tem = Profile.objects.filter(id_card__contains=valueword)
                    if keyword == '9':#入职时间
                        pro_tem = Profile.objects.filter(start_time__contains=valueword)

                    for p in pro_tem:
                        ans_tem.append(p.user)

                context = {}
                context['users'] = ans_tem
                return render(request, 'user_list.html', context)
        else:
            UserSelectForms = UserSelectForm()
            context = {}
            context['UserSelectForms'] = UserSelectForms
            return render(request, 'user_select.html', context)
    else:
        return redirect(reverse('login'))


def user_normal_select(request):

    usr = request.user
    if usr.is_authenticated:
        if request.method == 'POST':
            UserNormalSelectForms = UserNormalSelectForm(request.POST)
            if UserNormalSelectForms.is_valid():
                keyword = UserNormalSelectForms.cleaned_data['keyword']
                valueword = UserNormalSelectForms.cleaned_data['valueword']
                pro_tem = []
                ans_tem = []
                print(keyword, valueword)
                if keyword == '1':#姓名
                    ans_tem = User.objects.filter(Q(username__contains=valueword))
                else:
                    if keyword == '2':#职位
                        pro_tem = Profile.objects.filter(staff_type__contains=valueword)
                    if keyword == '3':#性别
                        tem = 'male' if valueword == '男' else 'female'
                        pro_tem = Profile.objects.filter(staff_gender=tem)
                    if keyword == '4':#年龄
                        pro_tem = Profile.objects.filter(staff_age__contains=valueword)
                    if keyword == '5':#籍贯
                        pro_tem = Profile.objects.filter(staff_home__contains=valueword)
                    if keyword == '6':#民族
                        pro_tem = Profile.objects.filter(staff_nationality__contains=valueword)
                    if keyword == '7':#电话
                        pro_tem = Profile.objects.filter(staff_tel__contains=valueword)

                    for p in pro_tem:
                        ans_tem.append(p.user)

                context = {}
                context['users'] = ans_tem
                return render(request, 'user_list.html', context)
        else:
            UserNormalSelectForms = UserNormalSelectForm()
            context = {}
            context['UserNormalSelectForms'] = UserNormalSelectForms
            return render(request, 'user_normal_select.html', context)
    else:
        return redirect(reverse('login'))






def leapyear(year):
    if year % 400 == 0:
        return True
    else:
        if year % 4 == 0 and year % 100 != 0:
            return True
    return False



