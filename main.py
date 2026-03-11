from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 飞书机器人与你的工具交互的 API
YOUR_MANAGER_API = "https://your-api.example.com"

@app.route('/feishu-events', methods=['POST'])
def handle_event():
    try:
        event_data = request.json
        print("Received Event Data: ", event_data)

        # 处理飞书 Challenge 验证
        if 'challenge' in event_data:
            return jsonify({"challenge": event_data['challenge']})

        # 处理普通事件
        if 'event' in event_data:
            event = event_data['event']
            event_type = event.get('type')
            
            # 处理消息事件
            if event_type == 'message.receive_v1':
                message_content = event['message'].get('content')
                user_id = event['sender']['id']
                handle_user_message(message_content, user_id)

        return jsonify({"msg": "ok"})

    except Exception as e:
        print("Error: ", str(e))
        return jsonify({"error": str(e)}), 500

def handle_user_message(message_content, user_id):
    """
    解析用户消息并执行操作
    """
    if message_content.startswith('/addtask'):
        # 解析任务添加指令
        _, task_info = message_content.split(' ', 1)
        project_name, task_name = task_info.split(' - ', 1)

        # 将任务同步到管理后台
        payload = {
            "project": project_name,
            "task": task_name,
            "status": "未开始",
        }
        response = requests.post(f"{YOUR_MANAGER_API}/tasks", json=payload)

        # 回复用户操作结果
        reply_to_user(user_id, f"任务 \"{task_name}\" 已成功添加到 \"{project_name}\"。")

    elif message_content.startswith('/viewtasks'):
        # 从管理后台查询任务
        response = requests.get(f"{YOUR_MANAGER_API}/tasks")
        task_list = response.json()  # 假设返回任务列表

        # 格式化任务并回复
        message = "当前所有任务：\n"
        for task in task_list["tasks"]:
            message += f"- [{task['status']}] {task['project']} - {task['name']}\n"
        reply_to_user(user_id, message)

def reply_to_user(user_id, content):
    """
    向用户发送消息
    """
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json",
    }
    payload = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": {"text": content},
    }
    result = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/messages",
        headers=headers,
        json=payload,
    )
    print("Send Message Response:", result.json())