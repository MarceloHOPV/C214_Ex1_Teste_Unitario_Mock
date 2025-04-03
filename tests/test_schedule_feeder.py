import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schedule_feeder import ScheduleFeeder

# -------------------- TESTES POSITIVOS --------------------

@pytest.mark.parametrize("db", [
    # 1. Caso padrão válido
    {"nomeDoProfessor": "Chris", "horarioDeAtendimento": "10:00 - 12:00", "periodo": "Noturno", "sala": "6", "predio": "2"},

    # 2. Sala mínima (1) no prédio mínimo (1)
    {"nomeDoProfessor": "Renzo", "horarioDeAtendimento": "08:00 - 09:00", "periodo": "Matutino", "sala": "1", "predio": "1"},

    # 3. Limite inferior da faixa do prédio (5/5 = 1 para prédio 1)
    {"nomeDoProfessor": "Marcelo", "horarioDeAtendimento": "09:00 - 10:00", "periodo": "Matutino", "sala": "5", "predio": "1"},

    # 4. Limite superior da faixa do prédio (10/5 = 2 para prédio 2)
    {"nomeDoProfessor": "Jonas", "horarioDeAtendimento": "11:00 - 12:00", "periodo": "Vespertino", "sala": "10", "predio": "2"},

    # 5. Nomes longos e strings com muitos caracteres
    {"nomeDoProfessor": "Professor Muito Muito Muito Legal", "horarioDeAtendimento": "13:00 - 15:00", "periodo": "Noturno", "sala": "15", "predio": "3"},

    # 6. Sala e prédio com números grandes (mas ainda válidos)
    {"nomeDoProfessor": "Mosca", "horarioDeAtendimento": "07:00 - 08:00", "periodo": "Integral", "sala": "100", "predio": "20"},

    # 7. Horário com formatação alternativa (ex: "9h às 11h")
    {"nomeDoProfessor": "Luiz Felipe", "horarioDeAtendimento": "9h às 11h", "periodo": "Noturno", "sala": "5", "predio": "1"},

    # 8. Sala exatamente no meio da faixa do prédio 2 (7.5 → sala 8)
    {"nomeDoProfessor": "Aline", "horarioDeAtendimento": "15:00 - 16:00", "periodo": "Vespertino", "sala": "8", "predio": "2"},

    # 9. Predio = 4, sala = 18 (intervalo entre 16 e 20 válido)
    {"nomeDoProfessor": "Paulo", "horarioDeAtendimento": "18:00 - 19:00", "periodo": "Noturno", "sala": "18", "predio": "4"},

    # 10. Professor com nome simples, tudo mínimo mas correto
    {"nomeDoProfessor": "Ana", "horarioDeAtendimento": "06:00 - 07:00", "periodo": "Matutino", "sala": "5", "predio": "1"},
], ids=[
    "Caso base",
    "Sala mínima no prédio 1",
    "Faixa inferior prédio 1",
    "Faixa superior prédio 2",
    "Nome e strings longas",
    "Sala e prédio grandes",
    "Horário alternativo",
    "Sala no meio da faixa prédio 2",
    "Sala dentro do prédio 4",
    "Caso com dados mínimos"
])
def test_schedule_valido(db):
    feeder = ScheduleFeeder(db)
    feeder.populate_page_schedule()
    assert isinstance(feeder.schedule, dict)

# -------------------- TESTES NEGATIVOS --------------------

@pytest.mark.parametrize("db, expected_message", [
    # 1. Faltando campo obrigatório ("periodo")
    (
        {"nomeDoProfessor": "Chris", "horarioDeAtendimento": "10:00 - 12:00", "sala": "6", "predio": "2"},
        "Erro de schema"
    ),

    # 2. Sala com ponto decimal
    (
        {"nomeDoProfessor": "Ana", "horarioDeAtendimento": "08:00 - 09:00", "periodo": "Matutino", "sala": "6.0", "predio": "2"},
        "Erro de valor"
    ),

    # 3. Prédio com vírgula como separador decimal
    (
        {"nomeDoProfessor": "Bruno", "horarioDeAtendimento": "09:00 - 10:00", "periodo": "Matutino", "sala": "6", "predio": "2,0"},
        "Erro de valor"
    ),

    # 4. Sala escrita por extenso
    (
        {"nomeDoProfessor": "Clara", "horarioDeAtendimento": "11:00 - 12:00", "periodo": "Vespertino", "sala": "seis", "predio": "2"},
        "Erro de valor"
    ),

    # 5. Campos de sala e prédio vazios
    (
        {"nomeDoProfessor": "Davi", "horarioDeAtendimento": "07:00 - 08:00", "periodo": "Integral", "sala": "", "predio": ""},
        "Erro de valor"
    ),

    # 6. Sala fora da faixa permitida para o prédio (ex: sala 13 no prédio 1)
    (
        {"nomeDoProfessor": "Elisa", "horarioDeAtendimento": "9h às 11h", "periodo": "Noturno", "sala": "13", "predio": "1"},
        "Erro de faixa"
    ),

    # 7. Prédio negativo
    (
        {"nomeDoProfessor": "Gustavo", "horarioDeAtendimento": "08:00 - 09:00", "periodo": "Matutino", "sala": "5", "predio": "-1"},
        "Erro de faixa"
    ),

    # 8. Sala negativa
    (
        {"nomeDoProfessor": "Helena", "horarioDeAtendimento": "10:00 - 11:00", "periodo": "Noturno", "sala": "-5", "predio": "2"},
        "Erro de faixa"
    ),

    # 9. Prédio como string vazia
    (
        {"nomeDoProfessor": "Igor", "horarioDeAtendimento": "07:00 - 08:00", "periodo": "Integral", "sala": "5", "predio": ""},
        "Erro de valor"
    ),

    # 10. Entrada inválida geral (None em vez de dict)
    (
        None,
        "Erro de tipo"
    ),
], ids=[
    "Campo ausente",
    "Sala com ponto",
    "Prédio com vírgula",
    "Sala como texto",
    "Campos vazios",
    "Sala fora da faixa",
    "Prédio negativo",
    "Sala negativa",
    "Prédio vazio",
    "Entrada None (não é dict)",
])
def test_schedule_invalido_com_mensagem(db, expected_message):
    with pytest.raises(ValueError, match=expected_message):
        feeder = ScheduleFeeder(db)
        feeder.populate_page_schedule()
