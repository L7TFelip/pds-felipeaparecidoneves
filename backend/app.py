from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados SQLite dentro do diretório instance/
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///petshop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Objeto SQLAlchemy que gerencia o banco de dados
db = SQLAlchemy(app)


# ==========================================
# MODELOS (TABELAS)
# ==========================================

class Dono(db.Model):
    __tablename__ = "donos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)

    # Relacionamento no Python (não cria coluna no banco)
    pets = db.relationship("Pet", backref="dono")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone
        }


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("donos.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "idade": self.idade,
            "dono_id": self.dono_id,
            "dono_nome": self.dono.nome  # Acessa o nome do dono via relacionamento
        }


# ==========================================
# ROTAS DE DONOS
# ==========================================

@app.route("/donos", methods=["GET"])
def listar_donos():
    donos = Dono.query.all()
    return jsonify([dono.to_dict() for dono in donos]), 200


@app.route("/donos/<int:dono_id>", methods=["GET"])
def buscar_dono(dono_id):
    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404
    return jsonify(dono.to_dict()), 200


@app.route("/donos", methods=["POST"])
def criar_dono():
    dados = request.json
    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    novo_dono = Dono(nome=dados["nome"], telefone=dados["telefone"])
    db.session.add(novo_dono)
    db.session.commit()

    return jsonify(novo_dono.to_dict()), 201


@app.route("/donos/<int:dono_id>", methods=["PUT"])
def atualizar_dono(dono_id):
    dados = request.json
    if not dados or "nome" not in dados or "telefone" not in dados:
        return jsonify({"erro": "Informe nome e telefone"}), 400

    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    dono.nome = dados["nome"]
    dono.telefone = dados["telefone"]
    db.session.commit()

    return jsonify(dono.to_dict()), 200


@app.route("/donos/<int:dono_id>", methods=["DELETE"])
def remover_dono(dono_id):
    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    db.session.delete(dono)
    db.session.commit()

    return jsonify({"mensagem": "Dono removido com sucesso"}), 200


# ==========================================
# ROTAS DE PETS
# ==========================================

@app.route("/pets", methods=["GET"])
def listar_pets():
    dono_id_param = request.args.get("dono_id")

    if dono_id_param:
        try:
            dono_id = int(dono_id_param)
            pets = Pet.query.filter_by(dono_id=dono_id).all()
        except ValueError:
            return jsonify({"erro": "dono_id invalido"}), 400
    else:
        pets = Pet.query.all()

    return jsonify([pet.to_dict() for pet in pets]), 200


@app.route("/pets/<int:pet_id>", methods=["GET"])
def buscar_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    return jsonify(pet.to_dict()), 200


@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.json
    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    # Desafio: verificar se o dono existe no banco
    dono = db.session.get(Dono, dados["dono_id"])
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    novo_pet = Pet(
        nome=dados["nome"],
        especie=dados["especie"],
        idade=dados["idade"],
        dono_id=dados["dono_id"]
    )

    db.session.add(novo_pet)
    db.session.commit()

    return jsonify(novo_pet.to_dict()), 201


@app.route("/pets/<int:pet_id>", methods=["PUT"])
def atualizar_pet(pet_id):
    dados = request.json
    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    pet = db.session.get(Pet, pet_id)
    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    dono = db.session.get(Dono, dados["dono_id"])
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    pet.nome = dados["nome"]
    pet.especie = dados["especie"]
    pet.idade = dados["idade"]
    pet.dono_id = dados["dono_id"]

    db.session.commit()

    return jsonify(pet.to_dict()), 200


@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def remover_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    db.session.delete(pet)
    db.session.commit()

    return jsonify({"mensagem": "Pet removido com sucesso"}), 200


if __name__ == "__main__":
    app.run(debug=True)
