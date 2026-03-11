from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# 你的管理工具 API 地址
YOUR_MANAGER_API = "https://your-api.example.com"

@app.route('/feishu-events', methods=['POST'])
def handle_event():
    """
    处理飞书发送的事件回调
    """
    try:
        # 解析飞书回调数据
        event_data = request.json
        print("Received Event Data: ", event_data)

        # Challenge 请求处理（飞书回调 URL 验证时发送）
        if 'challenge' in event_data:
            print("Received Challenge Request")
            return jsonify({"challenge": event_data['challenge']})

        # 普通事件处理
        if 'event' in event_data:
            event = event_data['event']
            event_type = event.get('type')
            print("Event Type: ", event_type)

            if event_type == 'message.receive_v1':
                message_content = event['message']['content']
                user_id = event['sender']['id']
                print("Message Content: ", message_content)
                handle_user_message(message_content, user_id)

        return jsonify({"msg": "ok"})

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


def handle_user_message(message_content, user_id):
    """
    根据用户发送的消息处理逻辑
    """
    try:
        if message_content.startswith('/addtask'):
            # 添加任务指令
            _, task_info = message_content.split(' ', 1)
            project_name, task_name = task_info.split(' - ', 1)

            # 同步到管理工具
            payload = {
                "project": project_name,
                "task": task_name,
                "status": "未开始",
            }
            response = requests.post(f"{YOUR_MANAGER_API}/tasks", json=payload)
            print("Task Add Response: ", response.json())

            # 回复用户
            reply_to_user(user_id, f"任务 \"{task_name}\" 已成功添加到 \"{project_name}\"。")

        elif message_content.startswith('/viewtasks'):
            # 查询任务指令
            response = requests.get(f"{YOUR_MANAGER_API}/tasks")
            task_list = response.json()  # 假设返回任务列表

            # 格式化任务并回复
            message = "当前所有任务：\n"
            for task in task_list["tasks"]:
                message += f"- [{task['status']}] {task['project']} - {task['name']}\n"
            reply_to_user(user_id, message)

    except Exception as e:
        print("Error in handle_user_message:", str(e))


def reply_to_user(user_id, content):
    """
    向飞书用户发送消息
    """
    try:
        headers = {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",
            "Content-Type": "application/json",
        }
        payload = {
            "receive_id": user_id,
            "msg_type": "text",
            "content": {"text": content},
        }
        response = requests.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers=headers,
            json=payload
        )
        print("Reply Message Response: ", response.json())
    except Exception as e:
        print("Error occurred while replying:", str(e))


if __name__ == '__main__':
    # 从 Render 动态环境变量获取端口，默认 3000
    port = int(os.environ.get("PORT", 3000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)