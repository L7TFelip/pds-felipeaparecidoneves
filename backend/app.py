from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///petshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS (COM RELACIONAMENTO)
# ==========================================

class Dono(db.Model):
    __tablename__ = "donos"
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    
    # Relacionamento 1-para-muitos
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
            "dono_nome": self.dono.nome  # Navegação via relacionamento
        }

# ==========================================
# ROTAS
# ==========================================

@app.route("/donos/<int:dono_id>/pets", methods=["GET"])
def listar_pets_do_dono(dono_id):
    dono = db.session.get(Dono, dono_id)
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404
    
    return jsonify([pet.to_dict() for pet in dono.pets])


if __name__ == "__main__":
    app.run(debug=True)

print("Mr - C")