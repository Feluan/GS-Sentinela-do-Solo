def ler_inteiro(mensagem, minimo, maximo):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo <= valor <= maximo:
                return valor
            print(f'Digite um número entre {minimo} e {maximo}.')
        except ValueError:
            print('Entrada inválida. Digite um número inteiro.')

def ler_float(mensagem, minimo=None, maximo=None):
    while True:
        try:
            valor = float(input(mensagem).strip().replace(',', '.'))
        except ValueError:
            print('Entrada inválida. Digite um número (ex.: 12,5).')
            continue
        if valor != valor or abs(valor) > 1000000000.0:
            print('Valor fora da escala física. Tente novamente.')
        elif minimo is not None and valor < minimo:
            print(f'O valor mínimo é {minimo}.')
        elif maximo is not None and valor > maximo:
            print(f'O valor máximo é {maximo}.')
        else:
            return valor

def ler_texto(mensagem, obrigatorio=True, tamanho_max=200):
    while True:
        texto = input(mensagem).strip()
        if texto == '' and obrigatorio:
            print('Este campo não pode ficar vazio.')
        elif len(texto) > tamanho_max:
            print(f'Use no máximo {tamanho_max} caracteres.')
        else:
            return texto

def ler_confirmacao(mensagem):
    while True:
        resposta = input(mensagem + ' (s/n): ').strip().lower()
        if resposta in ('s', 'sim'):
            return True
        if resposta in ('n', 'nao', 'não'):
            return False
        print("Responda com 's' para sim ou 'n' para não.")

def ler_coordenada(mensagem):
    print(mensagem)
    latitude = ler_float('  Latitude  (ex.: -23,5505): ', -90, 90)
    longitude = ler_float('  Longitude (ex.: -46,6333): ', -180, 180)
    return (latitude, longitude)
