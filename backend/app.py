# ==========================================
# ROTAS DE PETS
# ==========================================

# 1. LISTAR PETS (com filtro opcional por dono_id)
@app.route("/pets", methods=["GET"])
def listar_pets():
    dono_id_param = request.args.get("dono_id")

    if dono_id_param:
        # Query params chegam como string, converta para int
        try:
            dono_id = int(dono_id_param)
            pets = Pet.query.filter_by(dono_id=dono_id).all()
        except ValueError:
            return jsonify({"erro": "dono_id invalido"}), 400
    else:
        pets = Pet.query.all()

    # O to_dict() do Pet já inclui o 'dono_nome' sem precisar de JOIN
    return jsonify([pet.to_dict() for pet in pets]), 200


# 2. BUSCAR UM PET POR ID
@app.route("/pets/<int:pet_id>", methods=["GET"])
def buscar_pet(pet_id):
    pet = db.session.get(Pet, pet_id)

    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    return jsonify(pet.to_dict()), 200


# 3. CADASTRAR PET (com solução do Desafio)
@app.route("/pets", methods=["POST"])
def criar_pet():
    dados = request.json

    # Validação dos campos obrigatórios no JSON
    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    # DESAFIO: Verificar se o dono realmente existe antes de cadastrar
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


# 4. ATUALIZAR PET
@app.route("/pets/<int:pet_id>", methods=["PUT"])
def atualizar_pet(pet_id):
    dados = request.json

    if not dados or "nome" not in dados or "especie" not in dados or "idade" not in dados or "dono_id" not in dados:
        return jsonify({"erro": "Informe nome, especie, idade e dono_id"}), 400

    pet = db.session.get(Pet, pet_id)
    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    # Verifica se o novo dono informado existe
    dono = db.session.get(Dono, dados["dono_id"])
    if dono is None:
        return jsonify({"erro": "Dono nao encontrado"}), 404

    # Atualiza os atributos diretamente no objeto
    pet.nome = dados["nome"]
    pet.especie = dados["especie"]
    pet.idade = dados["idade"]
    pet.dono_id = dados["dono_id"]

    db.session.commit()

    return jsonify(pet.to_dict()), 200


# 5. REMOVER PET
@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def remover_pet(pet_id):
    pet = db.session.get(Pet, pet_id)

    if pet is None:
        return jsonify({"erro": "Pet nao encontrado"}), 404

    db.session.delete(pet)
    db.session.commit()

    return jsonify({"mensagem": "Pet removido com sucesso"}), 200
