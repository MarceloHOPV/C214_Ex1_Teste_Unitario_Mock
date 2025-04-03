from jsonschema import validate, ValidationError

class ScheduleFeeder:
    def __init__(self, schedule):
        self.schedule = schedule

    def populate_page_schedule(self):
        ScheduleVerify(self.schedule).validar_json_com_schema()
        ScheduleVerify(self.schedule).verificar_sala_predio()

        print("Schedule populado na página:")
        print(f"Professor: {self.schedule['nomeDoProfessor']}")
        print(f"Horário: {self.schedule['horarioDeAtendimento']}")
        print(f"Período: {self.schedule['periodo']}")
        print(f"Sala: {self.schedule['sala']}")
        print(f"Prédio: {self.schedule['predio']}")


class ScheduleVerify:
    def __init__(self, schedule):
        self.schedule = schedule

    def validar_json_com_schema(self) -> bool:
        schema = {
            "type": "object",
            "properties": {
                "nomeDoProfessor": {"type": "string"},
                "horarioDeAtendimento": {"type": "string"},
                "periodo": {"type": "string"},
                "sala": {"type": "string"},
                "predio": {"type": "string"},
            },
            "required": ["nomeDoProfessor", "horarioDeAtendimento", "periodo", "sala", "predio"]
        }

        # Verificação manual do tipo antes de validar com jsonschema
        if not isinstance(self.schedule, dict):
            raise ValueError("Erro de tipo")

        try:
            validate(instance=self.schedule, schema=schema)
            return True
        except ValidationError as e:
            raise ValueError("Erro de schema: campo ausente ou tipo inválido") from e

    def verificar_sala_predio(self) -> bool:
        try:
            sala = self.schedule["sala"]
            predio = self.schedule["predio"]

            # Verifica se são números inteiros válidos (permite sinal para tratar depois)
            if not sala.lstrip('-').isdigit() or not predio.lstrip('-').isdigit():
                raise ValueError("Erro de valor: sala ou prédio não são inteiros válidos")

            sala = int(sala)
            predio = int(predio)

            if sala < 1 or predio < 1:
                raise ValueError("Erro de faixa: valores negativos ou zero")

            if not ((sala / 5) <= predio and (sala / 5) >= (predio - 1)):
                raise ValueError("Erro de faixa: sala fora do intervalo permitido")

            return True

        except KeyError:
            raise ValueError("Erro de chave: campo ausente no dicionário")
