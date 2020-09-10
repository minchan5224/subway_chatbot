#작성 : 김민찬
from flask import Flask, request, jsonify, render_template
from pytz import timezone
from datetime import datetime
import subway_time

app = Flask(__name__)

@app.route('/migeum_d')
def migeum_d():
    return render_template('migeum_d.html')
@app.route('/migeum_h')
def migeum_h():
    return render_template('migeum_h.html')

@app.route('/message', methods=['POST'])
def Message():
    
    content = request.get_json()
    content = content['userRequest']
    content = content['utterance']
    KST = datetime.now(timezone('Asia/Seoul'))
    dataSend = subway_time.main_service(content, KST)
    
    
    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host='0.0.0.0')

