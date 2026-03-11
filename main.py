from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/feishu-events', methods=['POST'])
def handle_event():
    try:
        # 获取飞书发送的事件数据
        event_data = request.json
        print("Received Full Event Data: ", event_data)  # 打印接收到的完整数据

        # 处理飞书 "challenge" 验证（飞书回调验证时使用）
        if 'challenge' in event_data:
            print("[Challenge] Received Challenge Request: ", event_data['challenge'])
            return jsonify({"challenge": event_data['challenge']})

        # 处理普通事件
        if 'event' in event_data:
            event = event_data['event']  # 取出事件内容
            print("Event Data: ", event)

            if 'type' in event:
                event_type = event['type']
                print("Event Type: ", event_type)

                # 处理消息事件
                if event_type == 'message.receive_v1':
                    handle_message_event(event)
            else:
                print("[Error] Missing 'type' field in event.")

        else:
            print("[Error] Missing 'event' field in payload.")

        # 正常返回
        return jsonify({"msg": "ok"})

    except Exception as e:
        # 捕获任何异常并返回错误信息
        print("Exception occurred: ", str(e))
        return jsonify({"msg": "internal error", "error": str(e)}), 500


def handle_message_event(event):
    """
    用于处理消息事件的函数。
    """
    try:
        # 提取消息内容
        message = event.get('message', {})
        message_content = message.get('content', "")
        message_id = message.get('message_id', "")
        sender = event.get('sender', {}).get('id', "unknown sender")

        print(f"[Message Event] Received Message: {message_content}")
        print(f"[Message Event] Message ID: {message_id}")
        print(f"[Message Event] Sender ID: {sender}")

        # 这里可以执行自定义逻辑，例如回复消息或存储任务等操作
        # 示例：打印用户消息内容
        print(f"[Message] User said: {message_content}")

        # 示例：自动回复逻辑（未实现）
        # print("[Message] Auto-reply triggered...")

    except Exception as e:
        print("Error in handle_message_event: ", str(e))


if __name__ == '__main__':
    # 环境变量中读取 PORT，如果不存在则使用默认端口 3000
    port = int(os.environ.get("PORT", 3000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)