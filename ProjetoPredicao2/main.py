from flask import Flask, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from os.path import join, dirname
from dotenv import load_dotenv
import pandas as pd
import joblib
import os
from flask_cors import CORS
from datetime import datetime
import pymongo

dotenv_path = join(dirname(__file__), 'auth', '.env')
load_dotenv(dotenv_path)
MONGO_KEY = os.getenv("MONGO_KEY_URI")

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = MONGO_KEY
mongo = PyMongo(app)

@app.before_request
def check_mongo_connection():
    try:
        mongo.db.command("ping")
        print("Conexão com o MongoDB bem-sucedida!")
    except pymongo.errors.ConnectionFailure as e:
        print(f"Falha na conexão com o MongoDB: {str(e)}")
    except pymongo.errors.OperationFailure as e:
        print(f"Erro de operação no MongoDB: {str(e)}")

modelo = joblib.load(r'model\modelo_mlp.pkl')
print("Modelo carregado com sucesso!")

expected_features = [
    "Age", "Gender", "Ethnicity", "ParentalEducation", 
    "StudyTimeWeekly", "Absences", "Tutoring", "ParentalSupport",
    "Extracurricular", "Sports", "Music", "Volunteering"
]

@app.route('/')
def index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

@app.route("/predict", methods=["POST"])
def predict():
    try:
        dados = request.get_json()
        
        if not dados or not dados.get("features"):
            return jsonify({"erro": "Faltando 'features' no corpo da requisição ou requisição inválida"}), 400
        
        features = dados["features"]
        print("Features recebidas do frontend:", features)

        if len(features) != len(expected_features):
            return jsonify({"erro": f"Número incorreto de features. Esperado {len(expected_features)} features."}), 400

        if not all(isinstance(f, (int, float)) for f in features):
            return jsonify({"erro": "Todas as features devem ser números (int ou float)."}), 400

        entrada_modelo = pd.DataFrame([features], columns=expected_features)
        print("DataFrame com as features recebidas:\n", entrada_modelo)

        resultado = modelo.predict(entrada_modelo)
        print(f"Resultado da predição: {resultado}")

        dados_formulario = {
            "features": features,
            "Age": features[0],
            "Gender": features[1],
            "Ethnicity": features[2],
            "ParentalEducation": features[3],
            "StudyTimeWeekly": features[4],
            "Absences": features[5],
            "Tutoring": features[6],
            "ParentalSupport": features[7],
            "Extracurricular": features[8],
            "Sports": features[9],
            "Music": features[10],
            "Volunteering": features[11]
        }

        data_hora_atual = datetime.now()

        try:
            predicao = mongo.db.predicoes.insert_one({
                "entrada": features,
                "predicao": int(resultado[0]),
                "dados_formulario": dados_formulario,
                "data_hora": data_hora_atual
            })
            print("Predição armazenada no MongoDB com ID:", predicao.inserted_id)
        except pymongo.errors.PyMongoError as e:
            print(f"Erro ao armazenar no MongoDB: {str(e)}")
            return jsonify({"erro": "Falha ao armazenar a predição no banco de dados."}), 500

        return jsonify({"predicao": int(resultado[0])})
    except ValueError as e:
        print(f"Erro de valor durante a predição: {str(e)}")
        return jsonify({"erro": "Erro nos dados fornecidos."}), 400
    except (KeyError, TypeError) as e:
        print(f"Erro durante a predição: {str(e)}")
        return jsonify({"erro": "Erro nos dados fornecidos."}), 400
    except pymongo.errors.PyMongoError as e:
        print(f"Erro específico capturado: {str(e)}")
        return jsonify({"erro": "Erro no processamento dos dados ou no banco de dados."}), 500


@app.route('/dashboard')
def dashboard():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

@app.route('/dashboard_data', methods=['GET'])
def dashboard_data():
    data = list(mongo.db.predicoes.find({}, {"entrada": 1, "predicao": 1, "dados_formulario": 1, "data_hora": 1, "_id": 0}))
    
    if not data:
        return jsonify({
            "prediction_counts": {},
            "prediction_distribution": {},
            "distribution_data": {}
        })

    df = pd.DataFrame(data)
    formulario_data = pd.json_normalize(df["dados_formulario"])

    prediction_counts = df["predicao"].value_counts().to_dict()

    distribution_data = {
        "age_histogram": formulario_data["Age"].value_counts().to_dict(),
        "gender_bar_chart": formulario_data["Gender"].value_counts().to_dict(),
        "parental_education": formulario_data["ParentalEducation"].value_counts().to_dict(),
        "study_time_weekly": formulario_data["StudyTimeWeekly"].value_counts().to_dict(),
        "parental_support": formulario_data["ParentalSupport"].value_counts().to_dict(),
        "extracurricular": formulario_data["Extracurricular"].value_counts().to_dict()
    }

    # Se quiser criar uma distribuição separada por predição para um gráfico de pizza
    prediction_distribution = df["predicao"].value_counts().to_dict()

    dashboard_response = {
        "prediction_counts": prediction_counts,
        "prediction_distribution": prediction_distribution,
        "distribution_data": distribution_data
    }

    return jsonify(dashboard_response)


if __name__ == "__main__":
    app.run(debug=True)