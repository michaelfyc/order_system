from flask import request, session, Response
import json
from login.database import query_object, query_user_psd, edit_user_info
from application import app
import logging


@app.route("/api/editInfo", methods=["POST"])
def edit_info():
    """
    This is the EditInfo API
    Call this api to Edit information
    ---
    tags:
      - EditInformation
    parameters:
      - name: username
        in: body
        type: string
        required: true
        description: 新的用户名
        example: new_name
      - name: email
        in: body
        type: string
        required: true
        description: 新的邮箱
        example: new_email@email.com
      - name: changePassword
        in: body
        type: boolean
        required: true
        description: 是否修改密码
        example: 1
      - name: oldPassword
        in: body
        type: string
        required: true
        description: 旧密码
        example: 123456
      - name: newPassword
        in: body
        type: string
        required: true
        description: 新的密码
        example: 654321
    responses:
      200:
        description: 修改成功
        schema:
          properties:
            status:
                type: string
                description: 修改状态
                example: success
      403:
        description: 修改失败
        schema:
          properties:
            status:
                type: string
                description: 修改状态
                example: failed
            reason:
                type: string
                description: 错误原因
                example: 用户名已被占用
    """
    if request.method == "POST":
        # 获取数据 json
        data = request.get_json()
        back_json = dict()
        # 通过session 获取uid访问数据库
        new_info = dict()

        new_info = {
            'new_name': data.get('username'),
            'new_email': data.get('email')
        }
        uid = int(session['uid'])

        # 查询可否修改
        result = query_object(new_info['new_name'], '', new_info['new_email'], 'edit_info')
        back_json['status'] = 'failed'
        if result == 1:
            back_json['reason'] = '用户名被占用'
        elif result == 2:
            back_json['reason'] = '邮箱已注册'
        elif result == 3:
            edit_user_info(uid, 1, new_info)
            back_json['status'] = 'success'

        app.logger.info('%s change name to %s', session['username'],new_info['new_name'])

        # 如果用户申请修改密码
        if data.get('changePassword') == 1:
            # 检查密码
            old_password = data.get('oldPassword')

            # 数据库查询旧密码
            psd = query_user_psd(uid)['password']

            if psd == old_password:
                new_password = data.get('newPassword')
                new_info['new_psd'] = new_password
                edit_user_info(uid, 2, new_info)
                back_json['status'] = 'success'
            else:
                # 考虑优先级问题
                back_json['reason'] = '原密码输入错误'

        # 重新设置session
        session['username'] = new_info['new_name']
        session['email'] = new_info['new_email']

    return json.dumps(back_json), 200
