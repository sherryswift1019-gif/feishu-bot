from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/feishu-events', methods=['POST'])
def handle_event():
    # 获取飞书发送的事件数据
    event_data = request.json

    # 在终端打印接收到的事件内容
    print("Received Event Data: ", event_data)

    # Challenge 验证处理（飞书的初始验证请求需要返回 challenge 内容）
    if 'challenge' in event_data:
        return jsonify({"challenge": event_data['challenge']})

    # 如果是普通的事件（例如消息事件）
    if 'event' in event_data:
        print("Handling Event Type: ", event_data['event']['type'])
        # 根据具体事件类型进行处理，例如消息事件
        if event_data['event']['type'] == 'message.receive_v1':
            print("Message Data: ", event_data['event']['message'])

    # 返回200状态码
    return jsonify({"msg": "ok"})

if __name__ == '__main__':
    # 从环境变量中获取动态端口号，默认使用3000
    import os
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)