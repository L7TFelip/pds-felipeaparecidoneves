from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS
# ==========================================

class Dono(db.Model):
    __tablename__ = "donos"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    
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
    especie = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("donos.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "idade": self.idade,
            "dono_id": self.dono_id,
            "dono_nome": self.dono.nome
        }

# ==========================================
# FUNÇÕES DE VALIDAÇÃO (EXERCÍCIOS 1)
# ==========================================

def validar_dono(dados):
    erros = []
    if not isinstance(dados, dict):
        return ["O corpo da requisicao precisa ser um JSON de objeto"]
    
    nome = dados.get("nome")
    if not isinstance(nome, str) or nome.strip() == "":
        erros.append("O campo nome e obrigatorio e nao pode ser vazio")
        
    telefone = dados.get("telefone")
    if not isinstance(telefone, str) or telefone.strip() == "":
        erros.append("O campo telefone e obrigatorio e nao pode ser vazio")
        
    return erros


def validar_pet(dados):
    erros = []
    if not isinstance(dados, dict):
        return ["O corpo da requisicao precisa ser um JSON de objeto"]
    
    # Nome obrigatório e não vazio
    nome = dados.get("nome")
    if not isinstance(nome, str) or nome.strip() == "":
        erros.append("O campo nome e obrigatorio e nao pode ser vazio")
        
    # Espécie obrigatória e não vazia
    especie = dados.get("especie")
    if not isinstance(especie, str) or especie.strip() == "":
        erros.append("O campo especie e obrigatorio e nao pode ser vazio")
        
    # Idade: inteiro maior ou igual a zero
    idade = dados.get("idade")
    if not isinstance(idade, int) or isinstance(idade, bool) or idade < 0:
        erros.append("O campo idade deve ser um numero inteiro maior ou igual a zero")
        
    # Dono_id: inteiro e deve existir no banco
    dono_id = dados.get("dono_id")
    if not isinstance(dono_id, int) or isinstance(dono_id, bool):
        erros.append("O campo dono_id deve ser um numero inteiro")
    elif db.session.get(Dono, dono_id) is None:
        erros.append("Nao existe dono com esse dono_id")
        
    return erros

# ==========================================
# ROTAS DE DONOS
# ==========================================

@app.route("/donos", methods=["POST"])
def criar_dono():
    dados = request.json
    erros = validar_dono(dados)
    if erros:
        return jsonify({"erros": erros}), 400
        
    novo = Dono(nome=dados["nome"], telefone=dados["telefone"])
    db.session.add(novo)
    db.session.commit()
    return jsonify(novo.to_dict()), 201


@app.route("/donos/<int:dono_id>", methods=["PUT"])
def atualizar_dono(dono_id):
    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404
        
    dados = request.json
    erros = validar_dono(dados)
    if erros:
        return jsonify({"erros": erros}), 400
        
    dono.nome = dados["nome"]
    dono.telefone = dados["telefone"]
    db.session.commit()
    return jsonify(dono.to_dict())

# ==========================================
# ROTAS DE PETS (EXERCÍCIO 2)
# ==========================================

@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.json
    erros = validar_pet(dados)
    if erros:
        return jsonify({"erros": erros}), 400
        
    novo = Pet(
        nome=dados["nome"],
        especie=dados["especie"],
        idade=dados["idade"],
        dono_id=dados["dono_id"]
    )
    db.session.add(novo)
    db.session.commit()
    return jsonify(novo.to_dict()), 201


@app.route("/pets/<int:pet_id>", methods=["PUT"])
def atualizar_pet(pet_id):
    pet = db.session.get(Pet, pet_id)
    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404
        
    dados = request.json
    erros = validar_pet(dados)
    if erros:
        return jsonify({"erros": erros}), 400
        
    pet.nome = dados["nome"]
    pet.especie = dados["especie"]
    pet.idade = dados["idade"]
    pet.dono_id = dados["dono_id"]
    db.session.commit()
    return jsonify(pet.to_dict())


# Rotas auxiliares de GET e DELETE (mantidas intactas)
@app.route("/pets", methods=["GET"])
def listar_pets():
    pets = Pet.query.all()
    return jsonify([p.to_dict() for p in pets])


@app.route("/donos/<int:dono_id>/pets", methods=["GET"])
def listar_pets_do_dono(dono_id):
    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404
    return jsonify([pet.to_dict() for pet in dono.pets])


if __name__ == "__main__":
    app.run(debug=True)