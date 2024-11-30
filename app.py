# 파일 경로: app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# MongoDB 연결 설정
client = MongoClient('mongodb://localhost:27017/')
db = client.diary
entries_collection = db.entries

# 일기 생성 (Create)
@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.json
    if not data.get('date') or not data.get('title') or not data.get('content'):
        return jsonify({"error": "date, title, and content are required"}), 400

    entry = {
        "date": data['date'],
        "title": data['title'],
        "content": data['content'],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    result = entries_collection.insert_one(entry)
    return jsonify({"message": "Entry created", "id": str(result.inserted_id)}), 201

# 전체 일기 조회 (Read)
@app.route('/entries', methods=['GET'])
def get_entries():
    entries = []
    for entry in entries_collection.find():
        entries.append({
            "id": str(entry["_id"]),
            "date": entry["date"],
            "title": entry["title"],
            "content": entry["content"],
            "created_at": entry["created_at"],
            "updated_at": entry["updated_at"]
        })
    return jsonify(entries), 200

# 특정 날짜의 일기 조회 (Read by Date)
@app.route('/entries/<date>', methods=['GET'])
def get_entry_by_date(date):
    entries = entries_collection.find({"date": date})
    result = []
    for entry in entries:
        result.append({
            "id": str(entry["_id"]),
            "date": entry["date"],
            "title": entry["title"],
            "content": entry["content"],
            "created_at": entry["created_at"],
            "updated_at": entry["updated_at"]
        })
    if not result:
        return jsonify({"error": "No entries found for the specified date"}), 404
    return jsonify(result), 200

# 특정 일기 수정 (Update)
@app.route('/entries/<id>', methods=['PUT'])
def update_entry(id):
    data = request.json
    if not data.get('title') or not data.get('content'):
        return jsonify({"error": "title and content are required"}), 400

    updated_entry = {
        "title": data['title'],
        "content": data['content'],
        "updated_at": datetime.now()
    }
    result = entries_collection.update_one({"_id": ObjectId(id)}, {"$set": updated_entry})
    if result.matched_count == 0:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify({"message": "Entry updated"}), 200

# 특정 일기 삭제 (Delete)
@app.route('/entries/<id>', methods=['DELETE'])
def delete_entry(id):
    result = entries_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Entry not found"}), 404
    return jsonify({"message": "Entry deleted"}), 200

# 앱 실행
if __name__ == "__main__":
    app.run(host="10.20.0.128", port=5000, debug=True)
