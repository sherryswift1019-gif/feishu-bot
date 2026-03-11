from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/feishu-events', methods=['POST'])
def feishu_events():
    event_data = request.json
    # 验证飞书 Challenge Token
    if 'challenge' in event_data:
        return jsonify({"challenge": event_data['challenge']})

    # 处理业务逻辑
    print("Received event:", event_data)
    return jsonify({"msg": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)