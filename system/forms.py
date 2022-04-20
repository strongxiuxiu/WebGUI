from django import forms


class loginform(forms.Form):
    # 2、模板中的元素
    username = forms.CharField(required=True, min_length=1, error_messages={"min_length": "用户名最小长度为1"})
    # requird这个是错误码
    password = forms.CharField(required=True, min_length=6, error_messages={"min_length": "密码最小长度为6"})
    code = forms.CharField(required=True, min_length=4, error_messages={"min_length": "验证码最小长度为4"})
    token = forms.CharField(required=True, error_messages={"requird": "token不能为空"})
