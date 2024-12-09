

class LoadBar:
    def __init__(self, porcentaje):
        self.porcentaje = porcentaje

    def barra_de_carga(self):
        barra_len = 20
        filled_len = int((self.porcentaje / 100) * barra_len)
        barra = f'{self.cambiador_de_barra(self.porcentaje)}' * filled_len + '⬜' * (barra_len - filled_len)
        return f'\r{barra}    {int(self.porcentaje)}%'

    def cambiador_de_barra(self, porcentaje):
        if (porcentaje < 40):
            return '🟩'
        elif (porcentaje < 60):
            return '🟨'
        elif (porcentaje < 80):
            return '🟧'
        elif (porcentaje <= 100):
            return '🟥'
